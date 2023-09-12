#!/usr/bin/env python3

import subprocess

class Shell:
    def __init__(self, callback = None):
        self.reset(callback)

    def defaultCallback(self, line):
        print(line)

        return True

    def run(self, cmd):

        processData = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
        lines = []

        while True:
            line = processData.stdout.readline().decode('utf-8')
            if len(line) == 0:
                break

            if self.callback(line.strip()):
                lines.append(line.rstrip())

            if line == b'' or subprocess.Popen.poll(processData) == 0:
                processData.stdout.close()
                break
            
            if self.exit:
                print("exit: " + cmd)
                break
        
        return lines
    
    def reset(self, callback):
        self.exit = False
        if callback == None:
            self.callback = self.defaultCallback
        else:
            self.callback = callback
        
        return self

    def stop(self):
        self.exit = True

        return self
