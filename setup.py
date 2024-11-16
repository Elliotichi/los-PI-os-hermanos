import subprocess
from tendo import singleton


'''
# Enforce singleton pattern on setup (one node per device)
'''
try: 
	me = singleton.SingleInstance() 
except singleton.SingleInstanceException: exit()

# Dict for easy file pathing
scripts = {
	"Hub Node": "iot_project/hub_script.py",  
	"Berth Node" : "iot_project/room_script.py",
	"Weather Node": "iot_project/parking.py", 
	"Web Server": "server/server.js"
	}

'''
# Setup: get a deployment name and valid node selection from user
# Done via terminal to allow convenient setup (e.g. via SSH)
'''
def user_setup_prompts():
	global scripts
	print("=============== WARNING ===============") 
	print("Please ensure the deployment name is consistent across your deployment nodes.")
	print("Failure to do so will cause nodes to publish unretrievable messages.")
	print("=======================================")
	print("===== DEPLOYMENT CONFIG ======")
 
	deployment_name = deployment_name_prompt()
	node_type = node_type_prompt()
		
	return deployment_name, list(scripts.keys())[node_type-1]     

'''
# Prompt user for a 1-5 selection
'''
def node_type_prompt():  
	node_type = 0
	while not 0<node_type<6:
		try:
			node_type = int(input("\n[1] Hub \n[2] Room \n[3] Parking \n[4] Server\n Enter node type: "))
		except KeyboardInterrupt:
			quit()
		except ValueError:
			print("Sorry, please enter a valid number selection (1-4)")
	return node_type

'''
# Prompt user for a deployment name
'''
def deployment_name_prompt():
	try:
		deployment_name = input("Enter deployment name: ")	
	except KeyboardInterrupt:
		quit()
	return deployment_name

'''
# Get the deployment name and node type
# Write deployment name to config file, run correct script
'''
def main():
	deployment_name, node_type = user_setup_prompts()

	with open("config.txt", "w") as f:
		f.write(deployment_name)

	if node_type == "Web Server":
		try:
			subprocess.run(["node", "server/server.js"])
		except KeyboardInterrupt:
			quit()

	else:
		subprocess.run(["python", f"{scripts[node_type]}"])
		quit()
		

if __name__=="__main__":
	main()