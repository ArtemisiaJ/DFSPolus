# DFS Polus

Run python from automate (magnet automate) to open each casefile and parse the relational databases to obtain the OS of the exhibit processed. 
- If not present then mark as NO OS.
- If more than one OS we want all OS' present.
- Trawling script to determine OS of historic exhibits

# WindowsOS
Within the _Fragment Definition_ table, find _Operating System_ and take _fragment_definition_id_ then find the _fragment_definition_id_ within the _hit_fragment_ table.

# MacOS
Within the _Fragment Definition_ table, find _Operating System_ and take the _fragment_definition_id_ then find the _fragment_definition_id_ within the _hit_fragment_ table. In addition, within the _Fragment Definition_ table, find the _Version Number_ and take fragment_definition_id then find the fragment_definition_id within the hit_fragment table. Concatenate these.

# LinuxOS
Within the _Fragment Definition_ table, find _Operating System_ and take the _fragment_definition_id_ then find the _fragment_definition_id_ within the _hit_fragment_ table. In addition, within the _Fragment Definition_ table, find the _Operating System Version_ and take fragment_definition_id then find the fragment_definition_id within the hit_fragment table. Concatenate these.
