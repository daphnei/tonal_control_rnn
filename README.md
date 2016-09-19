# Recurrent Neural Nets for Music Generation

## Goals

## Resources 

### [RNN RBM] (https://github.com/tensorflow/magenta/blob/master/magenta/reviews/rnnrbm.md)
This blog post describes how to do polyphonic music generations using RBMs whose input is provided at each step by the RNN. Perhaps, we will incorporate RBMs once we have a basic architecute working. The sample code for the blog post also contains some convenient code for reading MIDI into vectors, which me might borrow. 

## To Do List
  1. Add MIDI to vector code
  2. data processing pipeline - ensure propagation melody_input time t+1 to all nodes
  3. Implement basic 1 layer LSTM network 
  4. design a cost function - use L2 norm to start
