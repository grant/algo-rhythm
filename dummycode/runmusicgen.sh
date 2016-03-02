seconds_to_generate=600
input_config=nonweb_config
output_file=nonweb_midi.mid
nohup python genmusic.py trained_configs/${input_config}  generated_music/${output_file} ${seconds_to_generate} &> generation_out.txt &

