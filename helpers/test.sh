#!/bin/bash


for ((i = 0; i < 5; i++)); do
  python3 client.py "test$i" &
  sleep 2
done

python3 client.py "Karol" &
sleep 1

python3 client.py "Julia" &
sleep 1

python3 client.py "Matus" &
sleep 1

sleep 1

read -p "Type 'kill' to terminate the runners: " user_input

if [ "$user_input" == "kill" ]; then
  ./helpers/killRunners.sh
  echo "killRunners.sh executed."
else
  echo "Command not recognized. Skipping killRunners.sh."
fi
