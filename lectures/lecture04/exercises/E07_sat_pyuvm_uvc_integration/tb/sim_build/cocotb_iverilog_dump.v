module cocotb_iverilog_dump();
initial begin
    $dumpfile("/home/Lasse-docker/02207-repo-fork-github/lectures/lecture04/exercises/E07_sat_pyuvm_uvc_integration/tb/sim_build/sat_filter.fst");
    $dumpvars(0, sat_filter);
end
endmodule
