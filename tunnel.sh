#!/bin/bash
ssh -t -t -L 22000:127.0.0.1:22000 'td-st\sdorco'@ie.technion.ac.il "ssh -L 22000:127.0.0.1:22 sdorco@innov.iem.technion.ac.il"
