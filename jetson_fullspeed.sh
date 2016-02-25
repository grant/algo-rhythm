#!/bash/bin

#Set the gpu clock to max rate
echo 998400000 > /sys/kernel/debug/clock/override.gbus/rate
echo 1 > /sys/kernel/debug/clock/override.gbus/state
cat /sys/kernel/debug/clock/gbus/rate

