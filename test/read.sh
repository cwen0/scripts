#!/bin/bash
read -p "please input a score:" score
echo -e "your score [$score] is judging by sys now"

if [ "$score" -ge "0" ] && [ "$score" -lt "60" ]; then
echo "sorry, you are lost!"
elif [ "$score" -ge "60" ] && [ "$score" -lt "85" ]; then
echo "just soso!"
elif [ "$score" -le "100" ] && [ "$score" -ge "85" ]; then
echo "good job!"
else
echo "input score is wrong, the range is [0-100]!"
fi
