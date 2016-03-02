num_iterations=100
output_config=nonweb_config
xml_source=training_xml_all
nohup python train.py trained_configs/${output_config} "`find ${xml_source}/ -name \* -type f`" ${num_iterations} &> training_out.txt &

