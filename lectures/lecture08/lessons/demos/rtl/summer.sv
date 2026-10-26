module summer #(parameter DATA_W = 8) (
  input  logic              clk,
  input  logic              rst,
  input  logic              in_valid,  // input data valid
  input  logic [DATA_W-1:0] in_data,   // input data
  output logic              out_valid, // output data valid
  output logic [DATA_W-1:0] out_data   // output data
);

  reg [DATA_W-1:0] prev_val;

  // Main loop
  always_ff @(posedge clk, negedge rst) begin
    if (rst === 1'b0) begin
      out_valid <= 'b0;
      out_data <= 'b0;
      prev_val <= 'b0;
    end else begin
      if (in_valid === 1'b1) begin
        out_valid <= 'b1;
        out_data <= in_data + prev_val;
        prev_val <= in_data;
      end else begin
        out_valid <= 'b0;
        out_data <= 'b0;
      end
    end
  end
endmodule: summer
