"""
for windows:
pip install --upgrade paramiko
or
pip uninstall pycrypto
pip install pycrypto
pip install ecdsa
"""
import Tkinter as tk
import tkMessageBox
import sys
import subprocess
import paramiko
import os
from os import listdir

TITLE_FONT = ("Helvetica", 18, "bold")
H2 = ("Helvetica", 12, "bold")
PORT = 22000
USER = 'sdorco'
PASSWORD = '123qwe!@#'

def sshExecute(host, user, password, runstring):
	hostname = host
	port = PORT
	username = USER
	password = PASSWORD
	command = runstring

	ssh = paramiko.SSHClient()
	ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	try:
		ssh.connect(username=user, password=password, hostname=hostname, port=port)
		print "Connected to " + str(hostname)
	except paramiko.SSHException as e:
		ssh.close()
		print e
		print "Error - Couldnt connect"
		print "Closed connection"
		

	try:
		stdin, stdout, stderr = ssh.exec_command(runstring)
		print "Executed command: " + str(runstring)
		for line in stdout:
			print '... ' + line.strip('\n')
	except paramiko.SSHException as e:
		ssh.close()
		print e
		print "Error - Couldnt execute command"
		print "Closed connection"

	ssh.close()
	print "Closed connection"

def readLog(log ,host, user, password):
	host = host
	port = PORT
	transport = paramiko.Transport((host, port))

	username = USER
	password = PASSWORD
	transport.connect(username = username, password = password)

	sftp = paramiko.SFTPClient.from_transport(transport)

	logs = {
		1: "exp1/out.log",
		2: "exp2/out.log",
		3: "exp3/out.log",
		4: "exp4/out.log",
		5: "exp5/out.log",
		6: "entropy/out.log",
		7: "merge/out.log"
	}

	try:
		log = sftp.file(logs[int(log)], mode="r", bufsize=-1)
	except IOError as e:
		print "Couldnt open log file"
		print "I/O error({0}): {1}".format(e.errno, e.strerror)

	sftp.close()
	transport.close()

	return log

class SampleApp(tk.Tk):

	def __init__(self, *args, **kwargs):
		tk.Tk.__init__(self, *args, **kwargs)

		# the container is where we'll stack a bunch of frames
		# on top of each other, then the one we want visible
		# will be raised above the others
		container = tk.Frame(self)
		container.pack(side="top", fill="both", expand=True)
		container.grid_rowconfigure(0, weight=1)
		container.grid_columnconfigure(0, weight=1)

		self.frames = {}
		for F in (StartPage, PageOne, PageTwo, PageThree, PageFour, PageFive):
			page_name = F.__name__
			frame = F(container, self)
			self.frames[page_name] = frame

			# put all of the pages in the same location;
			# the one on the top of the stacking order
			# will be the one that is visible.
			frame.grid(row=0, column=0, sticky="nsew")

		self.show_frame("StartPage")

	def show_frame(self, page_name):
		'''Show a frame for the given page name'''
		frame = self.frames[page_name]
		frame.tkraise()

class StartPage(tk.Frame):

	def __init__(self, parent, controller):
		tk.Frame.__init__(self, parent)
		self.controller = controller
		label = tk.Label(self, text="Formula Characterizer", font=TITLE_FONT)
		label.pack(side="top", fill="x", pady=10)

		button1 = tk.Button(self, text="Run Experiments",
							command=lambda: controller.show_frame("PageOne"))
		button2 = tk.Button(self, text="Analyze Entropy",
							command=lambda: controller.show_frame("PageTwo"))
		button3 = tk.Button(self, text="Merge Results",
							command=lambda: controller.show_frame("PageThree"))
		button4 = tk.Button(self, text="Read logs",
							command=lambda: controller.show_frame("PageFour"))
		button5 = tk.Button(self, text="Clear logs / results",
							command=lambda: controller.show_frame("PageFive"))		

		button1.pack(),
		button2.pack()
		button3.pack()
		button4.pack()
		button5.pack()


class PageOne(tk.Frame):

	def __init__(self, parent, controller):
		tk.Frame.__init__(self, parent)
		self.controller = controller
		label = tk.Label(self, text="Select an experiment", font=H2)
		label.pack(side="top", fill="x", pady=10)

		EXPS = [
			("First (Glucose - with/without DB reduction)", 1),
			("Second (Solvers with different LBD core cut)", 2),
			("Third (LBD Cut 5 vs. Clause size 12)", 3),
			("Fourth (Luby vs. Glucose style restarts)", 4),
			("Fifth (MiniSat with different decay factors)", 5)
		]

		v = tk.StringVar()
		v.set(1)

		for text, mode in EXPS:
			b = tk.Radiobutton(self, text=text, variable=v, value=mode)
			b.pack(anchor=tk.W)

		label = tk.Label(self, text="Instances directory", font=H2)
		label.pack(side="top", fill="x", pady=5)

		e = tk.Entry(self, width=50)
		e.pack()
		e.delete(0,tk.END)
		e.insert(0, "e.g 'instances' , '../instances', leave empty for current dir")

		label = tk.Label(self, text="Timeout", font=H2)
		label.pack(side="top", fill="x", pady=5)

		t = tk.Entry(self, width=50)
		t.pack()
		t.delete(0,tk.END)
		t.insert(0, "Timeout (seconds)")

		label = tk.Label(self, text="(optional) Formula list", font=H2)
		label.pack(side="top", fill="x", pady=5)

		l = tk.Entry(self, width=50)
		l.pack()
		l.delete(0,tk.END)
		l.insert(0,"e.g exp.csv (file must be on script dir) - Delete this if no file")


		label = tk.Label(self, text="Recursive search", font=H2)
		label.pack(side="top", fill="x", pady=5)

		rec = tk.IntVar()
		c = tk.Checkbutton(self, text="Recursive", variable=rec)
		c.pack()

		label = tk.Label(self, text="SSH Login Details:", font=H2)
		label.pack(side="top", fill="x", pady=5)

		host = tk.Entry(self, width=50)
		host.pack()
		host.delete(0,tk.END)
		host.insert(0, "innov.iem.technion.ac.il")

		user = tk.Entry(self, width=50)
		user.pack()
		user.delete(0,tk.END)
		user.insert(0, "sdorco")

		password = tk.Entry(self, show="*", width=50)
		password.pack()
		password.delete(0, tk.END)
		password.insert(0, "password")


		button = tk.Button(self, text="Run through SSH", pady=5,
						   command=lambda: self.runEXP(v.get(), e.get(), t.get(), l.get(), rec.get(), host.get(), user.get(), password.get()))
		button.pack()
		
		label = tk.Label(self, text="stderr:", font=H2)
		label.pack(side="top", fill="x", pady=5)

		scrollbar = tk.Scrollbar(self)
		scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

		self.text = tk.Text(self, height=3, width=30, yscrollcommand=scrollbar.set)
		self.text.pack(side="top", fill=tk.BOTH)
		self.text.insert(tk.END, '')

		scrollbar.config(command=self.text.yview)

		button = tk.Button(self, text="Read error log", pady=5,
						   command=lambda: self.readErrLog(v.get(), host.get(), user.get(), password.get()))
		button.pack()

		button = tk.Button(self, text="Back to start page", pady=5,
						   command=lambda: controller.show_frame("StartPage"))
		button.pack()
	
	def runEXP(self, exp, path, timeout, files, rec, host, user, password):
		runstring = ''
		exps = {
			1: 'exp1.py',
			2: 'exp2.py',
			3: 'exp3.py',
			4: 'exp4.py',
			5: 'exp5.py'
		}

		runstring = 'cd exp' +str(exp) + ';' + 'nohup python -u ' + exps[int(exp)] + ' '
		if path:
			runstring += '-p ' + str(path) + ' '
		if timeout:
			runstring += '-t ' + str(timeout) + ' '
		if files:
			runstring += '-l ' + str(files) + ' '
		if rec:
			runstring += '-r '

		log_out = 'out.log'
		log_err = 'err.log'
		runstring += '> ' + str(log_out) + ' 2> ' + str(log_err) + ' < /dev/null &'

		sshExecute(host,user,password,runstring)

	def readErrLog(self, log, host, user, password):
		host = host
		port = PORT
		transport = paramiko.Transport((host, port))

		username = USER
		password = PASSWORD
		transport.connect(username = username, password = password)

		sftp = paramiko.SFTPClient.from_transport(transport)

		logs = {
			1: "exp1/err.log",
			2: "exp2/err.log",
			3: "exp3/err.log",
			4: "exp4/err.log",
			5: "exp5/err.log",
		}

		try:
			log = sftp.file(logs[int(log)], mode="r", bufsize=-1)
			first = True
			self.text.delete(1.0, tk.END)
			for line in log:
				if first:
					self.text.insert("1.0", line)
					first = False
				else:
					self.text.insert(tk.END, line)
		except IOError as e:
			self.text.insert("1.0", "Couldnt open error log file\n")
			self.text.insert(tk.END, "I/O error({0}): {1}".format(e.errno, e.strerror))
		sftp.close()
		transport.close()

class PageTwo(tk.Frame):

	def __init__(self, parent, controller):
		tk.Frame.__init__(self, parent)
		self.controller = controller
		label = tk.Label(self, text="Analyze Entropies", font=H2)
		label.pack(side="top", fill="x", pady=10)

		label = tk.Label(self, text="Instances directory", font=H2)
		label.pack(side="top", fill="x", pady=5)

		e = tk.Entry(self, width=50)
		e.pack()
		e.delete(0,tk.END)
		e.insert(0, "Enter directory (for script dir leave empty)")

		label = tk.Label(self, text="Timeout", font=H2)
		label.pack(side="top", fill="x", pady=5)

		t = tk.Entry(self, width=50)
		t.pack()
		t.delete(0,tk.END)
		t.insert(0, "Timeout (seconds) - For each execution of model counter")

		label = tk.Label(self, text="(optional) Formula list", font=H2)
		label.pack(side="top", fill="x", pady=5)

		l = tk.Entry(self, width=50)
		l.pack()
		l.delete(0,tk.END)
		l.insert(0,"e.g exp.csv (file must be on script dir) - Delete this if no file")


		label = tk.Label(self, text="Recursive search", font=H2)
		label.pack(side="top", fill="x", pady=5)

		rec = tk.IntVar()
		c = tk.Checkbutton(self, text="Recursive", variable=rec)
		c.pack()

		label = tk.Label(self, text="SSH Login Details:", font=H2)
		label.pack(side="top", fill="x", pady=5)

		host = tk.Entry(self, width=50)
		host.pack()
		host.delete(0,tk.END)
		host.insert(0, "innov.iem.technion.ac.il")

		user = tk.Entry(self, width=50)
		user.pack()
		user.delete(0,tk.END)
		user.insert(0, "sdorco")

		password = tk.Entry(self, show="*", width=50)
		password.pack()
		password.delete(0, tk.END)
		password.insert(0, "password")

		button = tk.Button(self, text="Run through SSH",
						   command=lambda: self.runENT(e.get(), t.get(), l.get(), rec.get(), host.get(), user.get(), password.get() ))
		button.pack()

		label = tk.Label(self, text="stderr:", font=H2)
		label.pack(side="top", fill="x", pady=5)

		scrollbar = tk.Scrollbar(self)
		scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

		self.text = tk.Text(self, height=3, width=30, yscrollcommand=scrollbar.set)
		self.text.pack(side="top", fill=tk.BOTH)
		self.text.insert(tk.END, '')

		scrollbar.config(command=self.text.yview)

		button = tk.Button(self, text="Read error log", pady=5,
						   command=lambda: self.readErrLog(host.get(), user.get(), password.get()))
		button.pack()

		button = tk.Button(self, text="Back to start page", pady=5,
						   command=lambda: controller.show_frame("StartPage"))
		button.pack()

	def runENT(self, path, timeout, files, rec, host, user, password):
		runstring = 'cd entropy; nohup python -u main.py '
		if path:
			runstring += '-p ' + str(path) + ' '
		if timeout:
			runstring += '-t ' + str(timeout) + ' '
		if files:
			runstring += '-l ' + str(files) + ' '
		if rec:
			runstring += '-r '

		log_out = 'out.log'
		log_err = 'err.log'
		runstring += '> ' + str(log_out) + ' 2> ' + str(log_err) + ' < /dev/null &'

		sshExecute(host, user, password, runstring)
	
	def readErrLog(self,host, user, password):
		host = host
		port = PORT
		transport = paramiko.Transport((host, port))

		username = user
		password = password
		transport.connect(username = username, password = password)

		sftp = paramiko.SFTPClient.from_transport(transport)

		logs = {
			1: "entropy/err.log",
		}

		try:
			log = sftp.file(logs[1], mode="r", bufsize=-1)
			first = True
			self.text.delete(1.0, tk.END)
			for line in log:
				if first:
					self.text.insert("1.0", line)
					first = False
				else:
					self.text.insert(tk.END, line)
		except IOError as e:
			self.text.insert("1.0", "Couldnt open error log file\n")
			self.text.insert(tk.END, "I/O error({0}): {1}".format(e.errno, e.strerror))
		sftp.close()
		transport.close()


class PageThree(tk.Frame):

	def __init__(self, parent, controller):
		tk.Frame.__init__(self, parent)
		self.controller = controller
		label = tk.Label(self, text="Merge results", font=H2)
		label.pack(side="top", fill="x", pady=10)
		
		label = tk.Label(self, text="Select an experiment", font=H2)
		label.pack(side="top", fill="x", pady=10)

		EXPS = [
			("First (Glucose - with/without DB reduction)", 1),
			("Second (Solvers with different LBD core cut)", 2),
			("Third (LBD Cut 5 vs. Clause size 12)", 3),
			("Fourth (Luby vs. Glucose style restarts)", 4),
			("Fifth (MiniSat with different decay factors)", 5)
		]

		v = tk.StringVar()
		v.set(1)

		for text, mode in EXPS:
			b = tk.Radiobutton(self, text=text, variable=v, value=mode)
			b.pack(anchor=tk.W)
		
		label = tk.Label(self, text="SSH Login Details:", font=H2)
		label.pack(side="top", fill="x", pady=5)

		host = tk.Entry(self, width=50)
		host.pack()
		host.delete(0,tk.END)
		host.insert(0, "innov.iem.technion.ac.il")

		user = tk.Entry(self, width=50)
		user.pack()
		user.delete(0,tk.END)
		user.insert(0, "sdorco")

		password = tk.Entry(self, show="*", width=50)
		password.pack()
		password.delete(0, tk.END)
		password.insert(0, "password")

		button = tk.Button(self, text="Merge Results",
						   command=lambda: self.runMerge(v.get(), host.get(), user.get(), password.get() ))
		button.pack()

		button = tk.Button(self, text="Back to start page", pady=5,
						   command=lambda: controller.show_frame("StartPage"))
		button.pack()

	def runMerge(self, exp, host, user, password):
		runstring = 'cd merge; nohup python -u merge.py ' + str(int(exp))
		
		log_out = 'out.log'
		log_err = 'err.log'
		runstring += ' > ' + str(log_out) + ' 2> ' + str(log_err) + ' < /dev/null &'

		sshExecute(host, user, password, runstring)

	def readErrLog(self, host, user, password):
		host = host
		port = PORT
		transport = paramiko.Transport((host, port))

		username = user
		password = password
		transport.connect(username = username, password = password)

		sftp = paramiko.SFTPClient.from_transport(transport)

		logs = {
			1: "merge/err.log",
		}

		try:
			log = sftp.file(logs[1], mode="r", bufsize=-1)
			first = True
			self.text.delete(1.0, tk.END)
			for line in log:
				if first:
					self.text.insert("1.0", line)
					first = False
				else:
					self.text.insert(tk.END, line)
		except IOError as e:
			self.text.insert("1.0", "Couldnt open error log file\n")
			self.text.insert(tk.END, "I/O error({0}): {1}".format(e.errno, e.strerror))
		sftp.close()
		transport.close()

class PageFour(tk.Frame):

	def __init__(self, parent, controller):
		tk.Frame.__init__(self, parent)
		self.controller = controller
		label = tk.Label(self, text="Select a log to read", font=H2)
		label.pack(side="top", fill="x", pady=10)

		LOGS = [
			("First (Glucose - with/without DB reduction)", 1),
			("Second (Solvers with different LBD core cut)", 2),
			("Third (LBD Cut 5 vs. Clause size 12)", 3),
			("Fourth (Luby vs. Glucose style restarts)", 4),
			("Fifth (MiniSat with different decay factors)", 5),
			("Entropy analyzer logs", 6),
			("Merger logs", 7)
		]

		v = tk.StringVar()
		v.set(1)

		for text, mode in LOGS:
			b = tk.Radiobutton(self, text=text, variable=v, value=mode)
			b.pack(anchor=tk.W)
		
		label = tk.Label(self, text="SSH Login Details:", font=H2)
		label.pack(side="top", fill="x", pady=5)

		host = tk.Entry(self, width=50)
		host.pack()
		host.delete(0,tk.END)
		host.insert(0, "innov.iem.technion.ac.il")

		user = tk.Entry(self, width=50)
		user.pack()
		user.delete(0,tk.END)
		user.insert(0, "sdorco")

		password = tk.Entry(self, show="*", width=50)
		password.pack()
		password.delete(0, tk.END)
		password.insert(0, "password")

		button = tk.Button(self, text="Read logs",
						   command=lambda: self.setLogs(v.get(), host.get(), user.get(), password.get()))
		button.pack()
		
		label = tk.Label(self, text="Stdout:", font=H2)
		label.pack(side="top", fill="x", pady=5)

		scrollbar = tk.Scrollbar(self)
		scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

		self.text = tk.Text(self, height=10, width=30, yscrollcommand=scrollbar.set)
		self.text.pack(side="top", fill=tk.BOTH)
		self.text.insert(tk.END, '')

		scrollbar.config(command=self.text.yview)

		button = tk.Button(self, text="Back to start page", pady=5,
						   command=lambda: controller.show_frame("StartPage"))
		button.pack()

	def setLogs(self, log, host, user, password):
		host = host
		port = PORT
		transport = paramiko.Transport((host, port))

		username = USER
		password = PASSWORD
		transport.connect(username = username, password = password)

		sftp = paramiko.SFTPClient.from_transport(transport)

		logs = {
			1: "exp1/out.log",
			2: "exp2/out.log",
			3: "exp3/out.log",
			4: "exp4/out.log",
			5: "exp5/out.log",
			6: "entropy/out.log",
			7: "merge/out.log"
		}

		try:
			log = sftp.file(logs[int(log)], mode="r", bufsize=-1)
			first = True
			self.text.delete(1.0, tk.END)
			for line in log:
				if first:
					self.text.insert("1.0", line)
					first = False
				else:
					self.text.insert(tk.END, line)
		except IOError as e:
			self.text.insert("1.0", "Couldnt open log file\n")
			self.text.insert(tk.END, "I/O error({0}): {1}".format(e.errno, e.strerror))

		sftp.close()
		transport.close()

class PageFive(tk.Frame):
	def __init__(self, parent, controller):
		tk.Frame.__init__(self, parent)
		self.controller = controller

		label = tk.Label(self, text="SSH Login Details:", font=H2)
		label.pack(side="top", fill="x", pady=5)

		host = tk.Entry(self, width=50)
		host.pack()
		host.delete(0,tk.END)
		host.insert(0, "innov.iem.technion.ac.il")

		user = tk.Entry(self, width=50)
		user.pack()
		user.delete(0,tk.END)
		user.insert(0, "sdorco")

		password = tk.Entry(self, show="*", width=50)
		password.pack()
		password.delete(0, tk.END)
		password.insert(0, "password")

		label = tk.Label(self, text="Clear all logs", font=H2)
		label.pack(side="top", fill="x", pady=10)

		button = tk.Button(self, text="Clear logs",
						   command=lambda: self.deleteWarning('logs', host.get(), user.get(), password.get()))
		button.pack()

		label = tk.Label(self, text="Clear all results", font=H2)
		label.pack(side="top", fill="x", pady=10)

		button = tk.Button(self, text="Clear results",
						   command=lambda: self.deleteWarning('results', host.get(), user.get(), password.get()))
		button.pack()

		label = tk.Label(self, text="Kill all user processes", font=H2)
		label.pack(side="top", fill="x", pady=10)

		button = tk.Button(self, text="Kill processes",
						   command=lambda: self.deleteWarning('kill', host.get(), user.get(), password.get()))
		button.pack()

		button = tk.Button(self, text="Back to start page", pady=10,
						   command=lambda: controller.show_frame("StartPage"))
		button.pack()

	def deleteWarning(self, logsOrResults, host, user, password):
		result = tkMessageBox.askquestion("Delete", "Are you sure?", icon='warning')
		if result == 'yes':
			# delete logs
			if logsOrResults == 'logs':
				self.clearLogs(host, user, password)
			# delete results
			elif logsOrResults == 'results':
				self.clearResults(host, user, password)
			# kill processes
			elif logsOrResults == 'kill':
				self.killProc(host ,user, password)


	def clearLogs(self, host, user, password):
		host = host
		port = PORT
		transport = paramiko.Transport((host, port))

		username = USER
		password = PASSWORD
		transport.connect(username = username, password = password)

		sftp = paramiko.SFTPClient.from_transport(transport)

		logs = [
			"exp1/out.log",
			"exp1/err.log", 
			"exp2/out.log",
			"exp2/err.log",
			"exp3/out.log",
			"exp3/err.log",
			"exp4/out.log",
			"exp4/err.log",
			"exp5/out.log",
			"exp5/err.log",
			"entropy/err.log",
			"entropy/out.log",
			"merge/out.log",
			"merge/err.log"

		]

		for log in logs:
			try:
				sftp.remove(log)
			except IOError as e:
				print "Error deleting {0}".format(log)
				print "I/O error({0}): {1}".format(e.errno, e.strerror)

		sftp.close()
		transport.close()

	def clearResults(self, host, user, password):
		host = host
		port = PORT
		transport = paramiko.Transport((host, port))

		username = USER
		password = PASSWORD
		transport.connect(username = username, password = password)

		sftp = paramiko.SFTPClient.from_transport(transport)

		logs = [
			"exp1/output",
			"exp2/output",
			"exp3/output",
			"exp4/output",
			"exp5/output",
			"merge/output",
			"entropy/output/entropy",
			"entropy/output/histogram",
			"entropy/output/output",
			"entropy/output/sols",
			"entropy/output"
		]
		sftp.chdir('.')
		cwd = sftp.getcwd()
		for log in logs:
			files = sftp.listdir(os.path.join(cwd,log))
			# remove hidden files
			files = [x for x in files if not x.startswith('.')]
			for f in files:
				path = os.path.join(cwd,log,f)
				lstatout = str(sftp.lstat(path)).split()[0]
				if 'd' not in lstatout:
					try:
						sftp.remove(path)
						print "Removed {0}".format(path)
					except IOError as e:
						print "Error deleting {0}".format(path)
						print "I/O error({0}): {1}".format(e.errno, e.strerror)
		sftp.close()
		transport.close()

	def killProc(self, host, user, password):
		runstring = 'kill -9 -1'
		sshExecute(host, user, password, runstring)


if __name__ == "__main__":
	app = SampleApp()
	app.mainloop()