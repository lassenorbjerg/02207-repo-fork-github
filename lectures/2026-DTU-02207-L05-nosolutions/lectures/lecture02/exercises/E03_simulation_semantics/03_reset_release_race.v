`timescale 1ns/1ps

module counter_dut (
  input  wire       clk,
  input  wire       reset,
  output reg  [3:0] count
);

  always @(posedge clk) begin
    if (reset)
      count <= 4'd0;
    else
      count <= count + 1'b1;
  end

endmodule

module reset_release_race_tb;

  reg        clk;
  reg        reset;
  wire [3:0] count;

  counter_dut dut (
    .clk   (clk),
    .reset (reset),
    .count (count)
  );

  initial begin
    clk   = 0;
    reset = 1;

    // This occurs at the same time as a rising edge of clk.
    #15 reset = 0;

    #31 $finish;
  end

  always #5 clk = ~clk;

  initial begin
    $dumpfile("03_reset_release_race.fst");
    $dumpvars(0, reset_release_race_tb);
  end

endmodule
