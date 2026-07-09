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
from datetime import datetime

def debug_print(msg):
    """Print debug message with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    print(f"[{timestamp}] [DEBUG] {msg}")

staticimei = 0          #enter your imei here if you dont want to be asked every start
quickstart = False      #set to True to not need to confirm on script start, should be used in combination with staticimei

def run_command(cmd, description=""):
    """Run a command and capture output with debug logging"""
    if description:
        debug_print(f"Executing: {description}")
    debug_print(f"Command: {cmd}")
    
    result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout = result.stdout.decode('utf-8', errors='replace') if result.stdout else ""
    stderr = result.stderr.decode('utf-8', errors='replace') if result.stderr else ""
    
    debug_print(f"Return code: {result.returncode}")
    if stdout:
        debug_print(f"STDOUT:\n{stdout}")
    if stderr:
        debug_print(f"STDERR:\n{stderr}")
    
    return result, stdout, stderr

def bruteforceBootloader(increment):

    debug_print("=== Starting bruteforceBootloader function ===")
#    algoOEMcode = 0000000000000000
    algoOEMcode     = 1000000000000000  #base to start bruteforce from
    debug_print(f"Initial algoOEMcode: {algoOEMcode}")
    autoreboot      = False             #set this to True if you need to prevent the automatic reboot to system by the bootloader after x failed attempts, code will automatically set this to true if it detects a reboot by the bootloader
    debug_print(f"autoreboot initialized: {autoreboot}")
    autorebootcount = 4                 #reboot every x attemps if autoreboot is True, set this one below the automatic reboot by the bootloader
    debug_print(f"autorebootcount: {autorebootcount}")
    savecount       = 200               #save progress every 200 attempts, do not set too low to prevent storage wearout
    debug_print(f"savecount: {savecount}")
    unknownfail     = True              #fail if output is unknown, only switch to False if you have problems with this
    debug_print(f"unknownfail: {unknownfail}")

    failmsg = "check password failed"   #used to check if code is wrong
    debug_print(f"failmsg: {failmsg}")

    unlock=False
    n=0
    debug_print("Entering main bruteforce loop")
    while (unlock == False):
        debug_print(f"=== Loop iteration n={n} ===")
        debug_print(f"Testing algoOEMcode: {str(algoOEMcode).zfill(16)}")
        progress = round((algoOEMcode/10000000000000000)*100, 2)
        debug_print(f"Progress: {progress}%")
        
        cmd = f"fastboot oem unlock {str(algoOEMcode).zfill(16)}"
        debug_print(f"Executing fastboot unlock command")
        
        result, stdout, stderr = run_command(cmd, "Fastboot OEM unlock")
        output = stderr + stdout
        debug_print(f"Combined output length: {len(output)} characters")
        debug_print(f"Raw output:\n{output}")
        
        output_lower = output.lower()
        debug_print(f"Output lowercased for comparison")
        n+=1

        if 'success' in output_lower:
            debug_print("'success' found in output - unlocking successful!")
            bak = open("unlock_code.txt", "w")
            bak.write("Your saved bootloader code : "+str(algoOEMcode))
            bak.close()
            debug_print("Result saved to unlock_code.txt")
            return(algoOEMcode)
        
        if 'reboot' in output_lower:
            debug_print("'reboot' found in output - device has bruteforce protection")
            print("Target device has bruteforce protection!")
            print("Waiting for reboot and trying again...")
            
            debug_print("Executing: adb wait-for-device")
            run_command("adb wait-for-device", "ADB wait for device")
            
            debug_print("Executing: adb reboot bootloader")
            run_command("adb reboot bootloader", "ADB reboot to bootloader")
            
            debug_print("Waiting 10 seconds after reboot command...")
            time.sleep(10)
            debug_print("10 second wait completed")
            
            print("Device reboot requested, turning on reboot workaround.")
            autoreboot = True
            debug_print(f"autoreboot set to: {autoreboot}")
        
        if failmsg in output_lower:
            debug_print(f"'{failmsg}' found in output - code is wrong, continuing...")
            pass
        
        if 'success' not in output_lower and 'reboot' not in output_lower and failmsg not in output_lower and unknownfail:
            debug_print("Unknown output detected - none of success/reboot/failmsg found")
            debug_print(f"unknownfail is {unknownfail}, exiting...")
            print("Could not parse output.")
            print("Please check the output above yourself.")
            print("If you want to disable this feature, switch variable unknownfail to False")
            exit()

        if (n%savecount==0):
            debug_print(f"Saving progress at n={n}, algoOEMcode={algoOEMcode}")
            bak = open("unlock_code.txt", "w")
            bak.write("If you need to pick up where you left off,\nchange the algoOEMcode variable with #base comment to the following value :\n"+str(algoOEMcode))
            bak.close()
            debug_print("Progress saved to unlock_code.txt")

        if (n%autorebootcount==0 and autoreboot):
            debug_print(f"Rebooting at n={n} to prevent bootloader timeout")
            print("Rebooting to prevent bootloader from rebooting...")
            
            debug_print("Executing: fastboot reboot bootloader")
            run_command("fastboot reboot bootloader", "Fastboot reboot bootloader")
            
            debug_print("Waiting 10 seconds after reboot...")
            time.sleep(10)
            debug_print("10 second wait completed")

        debug_print(f"Incrementing algoOEMcode by {increment}")
        algoOEMcode += increment
        debug_print(f"New algoOEMcode: {algoOEMcode}")

        if (algoOEMcode > 10000000000000000):
            debug_print("algoOEMcode exceeded maximum value")
            print("OEM Code not found!\n")
            debug_print("Executing: fastboot reboot")
            run_command("fastboot reboot", "Fastboot reboot")
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

debug_print("=== Script started ===")
print('\n\n           Unlock Bootloader script - By SkyEmie_\' and programminghoch10')
print('\n\n  (You must enable USB DEBUGGING and OEM UNLOCK in the developer options of the target device...)')
print('  !!! All data will be erased !!! \n')
#input(' Press enter to detect device..\n')

debug_print("Executing: adb devices")
run_command("adb devices", "ADB devices list")

print("Please select \"Always allow from this computer\" in the adb dialog!")
debug_print("Waiting for ADB authorization...")

checksum = 1
debug_print("Starting IMEI validation loop")
while (checksum != 0):
    if staticimei == 0:
        debug_print("staticimei is 0, prompting for IMEI input")
        imei = int(input('Type IMEI: '))
    if staticimei > 0:
        debug_print(f"Using staticimei: {staticimei}")
        imei = staticimei
    debug_print(f"Calculating Luhn checksum for IMEI: {imei}")
    checksum = luhn_checksum(imei)
    if (checksum != 0):
        print('IMEI incorrect!')
        debug_print(f"Checksum result: {checksum} (expected 0)")
        if(staticimei > 0):
            debug_print("Exiting because staticimei is set and IMEI is incorrect")
            exit()
debug_print("IMEI validation passed")

increment = int(math.sqrt(imei)*1024)
debug_print(f"Calculated increment: {increment} (sqrt({imei}) * 1024)")

if quickstart==False:
    debug_print("quickstart is False, waiting for user confirmation")
    input('Press enter to reboot your device...\n')
else:
    debug_print("quickstart is True, skipping user confirmation")

debug_print("Executing: adb reboot bootloader")
run_command("adb reboot bootloader", "ADB reboot to bootloader")

debug_print("Waiting 10 seconds for device to enter bootloader...")
time.sleep(10)
debug_print("10 second wait completed")

#input('Press enter when your device is ready... (This may take time, depending on your phone)\n')

debug_print("Calling bruteforceBootloader function")
codeOEM = bruteforceBootloader(increment)

debug_print("Bruteforce completed, executing: fastboot getvar unlocked")
run_command("fastboot getvar unlocked", "Fastboot getvar unlocked")
#os.system('fastboot reboot')

print('\n\nDevice unlocked! OEM CODE: '+str(codeOEM)+'\n')
debug_print("Script completed successfully")
exit()
