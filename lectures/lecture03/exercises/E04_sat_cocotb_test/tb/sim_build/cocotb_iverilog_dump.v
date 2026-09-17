module cocotb_iverilog_dump();
initial begin
    $dumpfile("/home/Lasse-docker/02207-repo-fork/lectures/lecture03/exercises/E04_sat_cocotb_test/tb/sim_build/sat_filter.fst");
    $dumpvars(0, sat_filter);
end
endmodule
