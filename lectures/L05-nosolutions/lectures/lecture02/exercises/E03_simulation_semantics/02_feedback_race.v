`timescale 1ns/1ps

module adder_dut (
  input  wire       clk,
  input  wire       reset,
  input  wire [7:0] input_a,
  input  wire [7:0] input_b,
  output reg  [8:0] sum,
  output reg        ninth_bit_set
);

  wire [8:0] combinational_sum;

  assign combinational_sum = {1'b0, input_a} + {1'b0, input_b};

  always @(posedge clk) begin
    if (reset) begin
      sum           <= 9'd0;
      ninth_bit_set <= 1'b0;
    end
    else begin
      sum           <= combinational_sum;
      ninth_bit_set <= combinational_sum[8];
    end
  end

endmodule

module feedback_race_tb;

  reg        clk;
  reg        reset;
  reg  [7:0] input_a;
  reg  [7:0] input_b;
  wire [8:0] sum;
  wire       ninth_bit_set;

  localparam [7:0] BASE_A = 8'h80;
  localparam [7:0] BASE_B = 8'h90;

  // Global testbench state shared by two concurrent processes.
  reg [7:0] overflow_count;

  // Race-free reference for the result intended by the counter process.
  reg [8:0] debug_expected_sum;

  adder_dut dut (
    .clk           (clk),
    .reset         (reset),
    .input_a       (input_a),
    .input_b       (input_b),
    .sum           (sum),
    .ninth_bit_set (ninth_bit_set)
  );

  initial begin
    clk          = 0;
    reset        = 1;
    input_a      = 0;
    input_b      = 0;
    overflow_count = 0;
    debug_expected_sum = 0;

    #12 reset = 0;
    #100 $finish;
  end

  always #5 clk = ~clk;

  // Stimulus process: reads overflow_count to form A + (B + count).
  always @(posedge clk) begin
    if (reset) begin
      input_a <= 0;
      input_b <= 0;
    end
    else begin
      input_a <= BASE_A;
      input_b <= BASE_B + overflow_count;
    end
  end

  // Observer process: updates the shared counter on the same clock edge.
  always @(posedge clk) begin
    if (reset) begin
      overflow_count = 0;
      debug_expected_sum <= 0;
    end
    else begin
      if (ninth_bit_set)
        overflow_count = overflow_count + 1'b1;

      // This calculation always uses the counter after the optional increment.
      debug_expected_sum <= {1'b0, BASE_A}
                          + {1'b0, BASE_B}
                          + {1'b0, overflow_count};
    end
  end

  initial begin
    $dumpfile("02_feedback_race.fst");
    $dumpvars(0, feedback_race_tb);
  end

endmodule
