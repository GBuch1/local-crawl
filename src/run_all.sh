#!/bin/bash
# Copyright 2023 Westmont College, Mike Ryu mryu@westmont.edu
# CS 128 Fall 2023 Assignment 1 - Intermediate Text Processing
# A quick-and-dirty script to run through the sample data and Python unittests.

###############################
### DO NOT MODIFY THIS FILE ###
###############################

echo "Running pre-launch diagnostics ..."

echo -n "→ Check if in the git repository ....... "
if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "PASS"
else
  echo "FAIL"
  echo "  → Make sure you're working in the directory you cloned the repository to."
  exit 1
fi

echo -n "→ Check if in the 'src' directory ...... "
if pwd | grep -q "src"; then
  echo "PASS"
else
  echo "FAIL"
  echo "  → cd into 'src' directory before running this script."
  exit 2
fi

echo -n "→ Check 'python3' is a valid command ... "
if command -v python3 &>/dev/null; then
  echo "PASS"
  py="python3"
elif command -v python &>/dev/null; then
  echo "FAIL"
  echo "  → Using 'python' instead."
  py="python"
else
  echo "  → Python may not be installed here. I quit."
  exit 3
fi

printf "\nRunning file I/O with sample data ...\n"
for mode in {1..2}; do

  if [ "$mode" -eq 1 ]; then
    sub_dir="mode_1_word"
  elif [ "$mode" -eq 2 ]; then
    sub_dir="mode_2_twogram"
  fi

  for i in {0..4}; do
    echo "→ Using mode $mode with input 'word_0$i.in.txt' and output 'word_0$i.out.txt'"
    $py -m text_processing.freq_counter "$mode" "../data/word_0$i.in.txt" "../out/$sub_dir/word_0$i.out.txt"
  done

  for j in {1..6}; do
    echo "→ Using mode $mode with input 'twogram_0$j.in.txt' and output 'twogram_0$j.out.txt'"
    $py -m text_processing.freq_counter "$mode" "../data/twogram_0$j.in.txt" "../out/$sub_dir/twogram_0$j.out.txt"
  done
done

printf "\nRunning all Python unittests "
python3 -m unittest discover

printf "\nALL DONE :D\n"