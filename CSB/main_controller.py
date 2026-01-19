# main_controller.py

from add_candidate_00 import run_test
#from 01_checkin_candidate import run_checkin
#from 02_inviglator_startexam import run_startexam

import time

for i in range(30):
    print(f"\n🚀 第 {i+1} 次：建立 Candidate")
    run_test(i)
    time.sleep(1)

#for i in range(5):
#    print(f"\n✅ 第 {i+1} 次：Check-in Candidate")
#    run_checkin()
#    time.sleep(1)
#
#for i in range(5):
#    print(f"\n🟢 第 {i+1} 次：Invigilator Start Exam")
#    run_startexam()
#    time.sleep(1)