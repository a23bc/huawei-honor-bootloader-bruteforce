#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
SkyEmie_' 💜 https://github.com/SkyEmie
programminghoch10 https://github.com/programminghoch10
"""

import time
#from flashbootlib import test
import os
import subprocess
import math

staticimei = 0          #enter your imei here if you dont want to be asked every start
quickstart = False      #set to True to not need to confirm on script start, should be used in combination with staticimei

def bruteforceBootloader(increment):

    print("[DEBUG] Starting bruteforceBootloader function")
#    algoOEMcode = 0000000000000000
    algoOEMcode     = 1000000000000000  #base to start bruteforce from
    print(f"[DEBUG] Initial algoOEMcode: {algoOEMcode}")
    autoreboot      = False             #set this to True if you need to prevent the automatic reboot to system by the bootloader after x failed attempts, code will automatically set this to true if it detects a reboot by the bootloader
    print(f"[DEBUG] autoreboot initialized: {autoreboot}")
    autorebootcount = 4                 #reboot every x attemps if autoreboot is True, set this one below the automatic reboot by the bootloader
    print(f"[DEBUG] autorebootcount: {autorebootcount}")
    savecount       = 200               #save progress every 200 attempts, do not set too low to prevent storage wearout
    print(f"[DEBUG] savecount: {savecount}")
    unknownfail     = True              #fail if output is unknown, only switch to False if you have problems with this
    print(f"[DEBUG] unknownfail: {unknownfail}")
    
    failmsg = "check password failed"   #used to check if code is wrong
    print(f"[DEBUG] failmsg: {failmsg}")
    
    unlock=False
    n=0
    print("[DEBUG] Entering main bruteforce loop")
    while (unlock == False):
        print(f"[DEBUG] Loop iteration n={n}, testing algoOEMcode={algoOEMcode}")
        print("Bruteforce is running...\nCurrently testing code "+str(algoOEMcode).zfill(16)+"\nProgress: "+str(round((algoOEMcode/10000000000000000)*100, 2))+"%")
        print(f"[DEBUG] Executing command: fastboot oem unlock {str(algoOEMcode).zfill(16)}")
        output = subprocess.run("fastboot oem unlock " + str(algoOEMcode).zfill(16), shell=True, stderr=subprocess.PIPE).stderr.decode('utf-8')
        print(f"[DEBUG] Raw output received: {output}")
        print(output)
        output = output.lower()
        print(f"[DEBUG] Output lowercased: {output}")
        n+=1

        if 'success' in output:
            print("[DEBUG] 'success' found in output - unlocking successful!")
            bak = open("unlock_code.txt", "w")
            bak.write("Your saved bootloader code : "+str(algoOEMcode))
            bak.close()
            print("Your bruteforce result has been saved in \"unlock_code.txt\"")
            return(algoOEMcode)
        if 'reboot' in output:
            print("[DEBUG] 'reboot' found in output - device has bruteforce protection")
            print("Target device has bruteforce protection!")
            print("Waiting for reboot and trying again...")
            print("[DEBUG] Executing: adb wait-for-device")
            os.system("adb wait-for-device")
            print("[DEBUG] Executing: adb reboot bootloader")
            os.system("adb reboot bootloader")
            print("[DEBUG] Waiting 10 seconds after reboot command...")
            time.sleep(10)
            print("Device reboot requested, turning on reboot workaround.")
            autoreboot = True
            print(f"[DEBUG] autoreboot set to: {autoreboot}")
        if failmsg in output:
            print(f"[DEBUG] '{failmsg}' found in output - code is wrong, continuing...")
            #print("Code " + str(algoOEMcode) + " is wrong, trying next one...")
            pass
        if 'success' not in output and 'reboot' not in output and failmsg not in output and unknownfail:
            print("[DEBUG] Unknown output detected - none of success/reboot/failmsg found")
            # fail here to prevent continuing bruteforce on success or another error the script cant handle
            print("Could not parse output.")
            print("Please check the output above yourself.")
            print("If you want to disable this feature, switch variable unknownfail to False")
            exit()

        if (n%savecount==0):
            print(f"[DEBUG] Saving progress at n={n}, algoOEMcode={algoOEMcode}")
            bak = open("unlock_code.txt", "w")
            bak.write("If you need to pick up where you left off,\nchange the algoOEMcode variable with #base comment to the following value :\n"+str(algoOEMcode))
            bak.close()
            print("Your bruteforce progress has been saved in \"unlock_code.txt\"")

        if (n%autorebootcount==0 and autoreboot):
            print(f"[DEBUG] Rebooting at n={n} to prevent bootloader timeout")
            print("Rebooting to prevent bootloader from rebooting...")
            print("[DEBUG] Executing: fastboot reboot bootloader")
            os.system('fastboot reboot bootloader')
            print("[DEBUG] Waiting 10 seconds after reboot...")
            time.sleep(10)

        print(f"[DEBUG] Incrementing algoOEMcode by {increment}")
        algoOEMcode += increment
        print(f"[DEBUG] New algoOEMcode: {algoOEMcode}")

        if (algoOEMcode > 10000000000000000):
            print("[DEBUG] algoOEMcode exceeded maximum value")
            print("OEM Code not found!\n")
            print("[DEBUG] Executing: fastboot reboot")
            os.system("fastboot reboot")
            exit()

def luhn_checksum(imei):
    def digits_of(n):
        return [int(d) for d in str(n)]
    digits = digits_of(imei)
    oddDigits = digits[-1::-2]
    evenDigits = digits[-2::-2]
    checksum = 0
    checksum += sum(oddDigits)
    for i in evenDigits:
        checksum += sum(digits_of(i*2))
    return checksum % 10


# Bruteforce setup:

print('\n\n           Unlock Bootloader script - By SkyEmie_\' and programminghoch10')
print('[DEBUG] Script started')
print('\n\n  (You must enable USB DEBUGGING and OEM UNLOCK in the developer options of the target device...)')
print('  !!! All data will be erased !!! \n')
#input(' Press enter to detect device..\n')

print('[DEBUG] Executing: adb devices')
os.system('adb devices')

print("Please select \"Always allow from this computer\" in the adb dialog!")
print('[DEBUG] Waiting for ADB authorization...')

checksum = 1
print('[DEBUG] Starting IMEI validation loop')
while (checksum != 0):
    if staticimei == 0: 
        print('[DEBUG] staticimei is 0, prompting for IMEI input')
        imei = int(input('Type IMEI: '))
    if staticimei > 0:
        print(f'[DEBUG] Using staticimei: {staticimei}')
        imei = staticimei
    print(f'[DEBUG] Calculating Luhn checksum for IMEI: {imei}')
    checksum = luhn_checksum(imei)
    if (checksum != 0):
        print('IMEI incorrect!')
        print(f'[DEBUG] Checksum result: {checksum} (expected 0)')
        if(staticimei > 0):
            print('[DEBUG] Exiting because staticimei is set and IMEI is incorrect')
            exit()
print('[DEBUG] IMEI validation passed')
increment = int(math.sqrt(imei)*1024)
print(f'[DEBUG] Calculated increment: {increment} (sqrt({imei}) * 1024)')
if quickstart==False:
    print('[DEBUG] quickstart is False, waiting for user confirmation')
    input('Press enter to reboot your device...\n')
else:
    print('[DEBUG] quickstart is True, skipping user confirmation')
print('[DEBUG] Executing: adb reboot bootloader')
os.system('adb reboot bootloader')
print('Waiting 10 seconds for device to enter bootloader...')
print('[DEBUG] Sleeping for 10 seconds...')
time.sleep(10)
print('[DEBUG] 10 second wait completed')
#input('Press enter when your device is ready... (This may take time, depending on your phone)\n')

print('[DEBUG] Calling bruteforceBootloader function')
codeOEM = bruteforceBootloader(increment)

print('[DEBUG] Bruteforce completed, executing: fastboot getvar unlocked')
os.system('fastboot getvar unlocked')
#os.system('fastboot reboot')

print('\n\nDevice unlocked! OEM CODE: '+str(codeOEM)+'\n')
print('[DEBUG] Script completed successfully')
exit()
