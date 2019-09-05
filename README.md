# zoning_config
Text-based utility for managing FC zoning configurations

This is the first version, limited to the following
* Cisco MDS zoning configurations only
* WWNs only
* All WWNs defined as device-aliases 
* Single initiator / multi target style zoning only

The script takes one input, the name of a CSV file that contains the per-line definitions of:
* targets (first columm == "t")
* initiators (first column == "i")
* zones (first column == "z")
* zoneset (first column == "zs")

For example, the following input file:
<pre>
t,mytarget1,"0a,0c","20:00:00:00:00:00:00:01,20:00:00:00:00:00:00:02"
t,mytarget2,"0e,0g","20:01:00:00:00:00:00:01,20:01:00:00:00:00:00:02"
t,mytarget3,"0e,0g","20:01:00:00:00:00:00:01,20:01:00:00:00:00:00:02"
i,myinitiator1,"hba1","20:08:00:00:00:00:00:02"
i,myinitiator2,"hba1","20:08:00:00:00:00:00:02"
zs,myzoneset,10
z,"mytarget1,mytarget2,myinitiator1"
z,"myinitiator2,mytarget1"
</pre>

Will yield the following output to stdout:
<pre>
### device-aliases
device-alias name mytarget2_0e pwwn 20:01:00:00:00:00:00:01
device-alias name mytarget2_0g pwwn 20:01:00:00:00:00:00:02
device-alias name mytarget3_0e pwwn 20:01:00:00:00:00:00:01
device-alias name mytarget3_0g pwwn 20:01:00:00:00:00:00:02
device-alias name mytarget1_0a pwwn 20:00:00:00:00:00:00:01
device-alias name mytarget1_0c pwwn 20:00:00:00:00:00:00:02
device-alias name myinitiator2_hba1 pwwn 20:08:00:00:00:00:00:02
device-alias name myinitiator1_hba1 pwwn 20:08:00:00:00:00:00:02
### zones
zone name myinitiator2_hba1_mytarget1 vsan 10
 member device-alias myinitiator2_hba1
 member device-alias mytarget1_0a
 member device-alias mytarget1_0c
zone name myinitiator1_hba1_mytarget2 vsan 10
 member device-alias myinitiator1_hba1
 member device-alias mytarget2_0e
 member device-alias mytarget2_0g
zone name myinitiator1_hba1_mytarget1 vsan 10
 member device-alias myinitiator1_hba1
 member device-alias mytarget1_0a
 member device-alias mytarget1_0c
### zoneset
zoneset name myzoneset vsan 10
 member myinitiator2_hba1_mytarget1
 member myinitiator1_hba1_mytarget2
 member myinitiator1_hba1_mytarget1
 exit
zoneset activate myzoneset vsan 10
</pre>

Beware, applying this command output to the CLI of a Cisco MDS switch will do the following:
* Overwrite device-aliases that already exist
* Add members to zones that already exist
* Add zones to zonesets that already exist
* Change the active zoneset if different

Features coming in later releases will include:
* Cisco FC-alias zoning
* Brocade zoning
* Parse existing configuration
* Better internal data structures
