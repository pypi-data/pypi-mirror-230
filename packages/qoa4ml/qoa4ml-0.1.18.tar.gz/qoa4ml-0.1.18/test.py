from __future__ import annotations
from qoa4ml.QoaClient import QoaClient
import argparse, time, random, sys, traceback
from threading import Thread

clientConf1 = { 
    "client":{
        "client_id": "aaltosea1",
        "instance_name": "data_handling01",
        "stage_id": "Gateway",
        "method": "REST",
        "application": "test",
        "role": "ml"
    },
    "registration_url":"http://localhost:5010/registration"
}

clientConf2 = { 
    "client":{
         "client_id": "aaltosea2",
        "instance_name": "data_processing01",
        "stage_id": "Processing",
        "method": "REST",
        "application": "test",
        "role": "ml"
    },
    "registration_url":"http://localhost:5010/registration"
}

clientConf3 = { 
    "client":{
        "client_id": "aaltosea3",
        "instance_name": "ML01",
        "stage_id": "ML",
        "method": "REST",
        "application": "test",
        "role": "ml"
    },
    "registration_url":"http://localhost:5010/registration"
}

clientConf4 = { 
    "client":{
        "client_id": "aaltosea4",
        "instance_name": "ML02",
        "stage_id": "ML",
        "method": "REST",
        "application": "test",
        "role": "ml"
    },
    "registration_url":"http://localhost:5010/registration"
}

clientConf5 = { 
    "client":{
        "client_id": "aaltosea5",
        "instance_name": "Agg01",
        "stage_id": "Aggregate",
        "method": "REST",
        "application": "test",
        "role": "ml"
    },
    "registration_url":"http://localhost:5010/registration"
}



client1 = QoaClient(config_dict=clientConf1)
client2 = QoaClient(config_dict=clientConf2)
client3 = QoaClient(config_dict=clientConf3)
client4 = QoaClient(config_dict=clientConf4)
client5 = QoaClient(config_dict=clientConf5)
# client5.process_monitor_start(1)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Node Monitoring")
    parser.add_argument('--th', help='Number of thread', default=1)
    parser.add_argument('--sl', help='Sleep time', default=-1)
    parser.add_argument('--client', help='Client config file', default="./conf.json")
    args = parser.parse_args()

    concurrent = int(args.th)
    time_sleep = float(args.sl)



    def sender(num_thread):
        count = 0
        error = 0
        start_time = time.time()
        while (time.time() - start_time < 1000):
            try:
                client1.timer()
                print("This is thread: ",num_thread, "Starting request: ", count)
                client1.observeMetric("metric1", random.randint(1, 100), 0)
                client1.observeMetric("metric2", random.randint(1, 100), 0)
                client1.observeMetric("image_width", random.randint(1, 100), 1)
                client1.observeMetric("image_height", random.randint(1, 100), 1)
                client1.observeMetric("object_width", random.randint(1, 100), 1)
                client1.observeMetric("object_height", random.randint(1, 100), 1)
                client1.timer()
                report_1 = client1.report()
                # print("Thread - ",num_thread, " Response1:", report_1)
                
                client2.importPReport(report_1)
                client2.timer()
                print("This is thread: ",num_thread, "Starting request: ", count)
                client2.observeMetric("metric1", random.randint(1, 100), 0)
                client2.observeMetric("metric2", random.randint(1, 100), 0)
                client2.observeMetric("image_width", random.randint(1, 100), 1)
                client2.observeMetric("image_height", random.randint(1, 100), 1)
                client2.observeMetric("object_width", random.randint(1, 100), 1)
                client2.observeMetric("object_height", random.randint(1, 100), 1)
                client2.timer()
                report_2 = client2.report()
                # print("Thread - ",num_thread, " Response2:", report_2)


                client3.importPReport(report_2)
                client3.timer()
                print("This is thread: ",num_thread, "Starting request: ", count)
                client3.observeInferenceMetric("confidence", random.randint(1, 100))
                client3.observeInferenceMetric("accuracy", random.randint(1, 100))
                client3.timer()
                report_3 = client3.report()
                # print("Thread - ",num_thread, " Response3:", report_3)

                client4.importPReport(report_2)
                client4.timer()
                print("This is thread: ",num_thread, "Starting request: ", count)
                client4.observeInferenceMetric("confidence", random.randint(1, 100))
                client4.observeInferenceMetric("accuracy", random.randint(1, 100))
                client4.timer()
                report_4 = client4.report()
                # print("Thread - ",num_thread, " Response4:", report_4)

                client5.importPReport([report_3,report_4])
                client5.timer()
                print("This is thread: ",num_thread, "Starting request: ", count)
                client5.observeInferenceMetric("confidence", random.randint(1, 100))
                client5.observeInferenceMetric("accuracy", random.randint(1, 100))
                client5.timer()
                report_5 = client5.report(submit=True)
                # print("Thread - ",num_thread, " Response5:", report_5)
            except Exception as e:
                error +=1
                qoaLogger.error("Error {} in merge_dict: {}".format(type(e),e.__traceback__))
                traceback.print_exception(*sys.exc_info())
            count += 1
            if time_sleep == -1:
                time.sleep(1)
            else:
                time.sleep(time_sleep)

    for i in range(concurrent):
        t = Thread(target=sender,args=[i])
        t.start()
