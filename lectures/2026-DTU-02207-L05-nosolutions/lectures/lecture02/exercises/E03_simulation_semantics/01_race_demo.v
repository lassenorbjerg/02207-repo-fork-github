`timescale 1ns/1ps

module race_demo;

  reg clk;
  reg value;
  reg sampled;

  initial begin
    clk     = 0;
    value   = 0;
    sampled = 0;
  end

  always #5 clk = ~clk;

  // This blocking assignment updates value immediately.
  always @(posedge clk)
    value = ~value;

  // This nonblocking assignment samples value now and updates sampled later.
  always @(posedge clk)
    sampled <= value;

  initial begin
    $dumpfile("01_race_demo.fst");
    $dumpvars(0, race_demo);

    #51;
    $finish;
  end

endmodule
