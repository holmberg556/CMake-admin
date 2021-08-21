cmake_minimum_required(VERSION 3.20)
project(simple)

function(x_fun)
  y_fun()
endfunction()

function(y_fun)
  z_fun()
endfunction()

function(z_fun)
  message(STATUS "This is z_fun")
endfunction()

macro(p_macro)
  y_fun()
endmacro()

add_subdirectory(subdirA)
add_subdirectory(subdirB)
add_subdirectory(subdirC)

z_fun()

function(call_fun_and_macro)
  w_fun()
  w_macro()
endfunction()

function(w_fun)
  z_fun()
endfunction()

macro(w_macro)
  z_fun()
endmacro()


call_fun_and_macro()
