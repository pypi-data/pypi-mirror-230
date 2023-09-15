from prometheus_client import Gauge

# PSU

GAEU_PSU_V_CCD = Gauge("gaeu_psu_v_ccd", "PSU voltage for CCD [V]")
GAEU_PSU_I_CCD = Gauge("gaeu_psu_i_ccd", "PSU current for CCD [A]")
GAEU_PSU_V_CLK = Gauge("gaeu_psu_v_clk", "PSU voltage for CLK [V]")
GAEU_PSU_I_CLK = Gauge("gaeu_psu_i_clk", "PSU current for CLK [A]")
GAEU_PSU_V_AN1 = Gauge("gaeu_psu_v_an1", "PSU voltage for AN1 [V]")
GAEU_PSU_I_AN1 = Gauge("gaeu_psu_i_an1", "PSU current for AN1 [A]")
GAEU_PSU_V_AN2 = Gauge("gaeu_psu_v_an2", "PSU voltage for AN2 [V]")
GAEU_PSU_I_AN2 = Gauge("gaeu_psu_i_an2", "PSU current for AN2 [A]")
GAEU_PSU_V_AN3 = Gauge("gaeu_psu_v_an3", "PSU voltage for AN3 [V]")
GAEU_PSU_I_AN3 = Gauge("gaeu_psu_i_an3", "PSU current for AN3 [A]")
GAEU_PSU_V_DIG = Gauge("gaeu_psu_v_dig", "PSU voltage for DIG [V]")
GAEU_PSU_I_DIG = Gauge("gaeu_psu_i_dig", "PSU current for DIG [A]")

GAEU_PSU_OVP = Gauge("gaeu_psu_ovp", "PSU Over-Voltage Protection (OVP) [V]")
GAEU_PSU_V_SETPOINT = Gauge("gaeu_psu_v_setpoint", "PSU voltage setpoint [V]")
GAEU_PSU_OCP = Gauge("gaeu_psu_ocp", "PSU Over-Current Protection (OCP) [A]")
GAEU_PSU_I_SETPOINT = Gauge("gaeu_psu_i_setpoint", "PSU current setpoint [A]")

# cRIO

GAEU_STANDBY = Gauge("gaeu_standby", "Indicates whether or not the AEU is in stand-by mode")
GAEU_SELFTEST = Gauge("gaeu_selftest", "Indicates whether or not the AEU is in self-test mode")
GAEU_FC_TVAC = Gauge("gaeu_fc_tvac", "Indicates whether or not the AEU is in functional check and TVAC mode")
GAEU_ALIGNMENT = Gauge("gaeu_alignment", "Indicates whether or not the AEU is in alignment mode")

GAEU_PWR_NFEE_STATUS = Gauge("gaeu_pwr_nfee_status", "Indicates whether or not the N-CAM is selected")
GAEU_PWR_FFEE_STATUS = Gauge("gaeu_pwr_ffee_status", "Indicates whether or not the F-CAM is selected")

GAEU_S_VOLTAGE_OOR = Gauge("gaeu_s_voltage_oor", "Indicates where or not the secondary voltage generation is "
                                                 "out-of-range")
GAEU_S_CURRENT_OOR = Gauge("gaeu_s_current_oor", "Indicates where or not the secondary voltage generation is "
                                                 "out-of-range")
GAEU_SYNC_GF = Gauge("gaeu_sync_gf", "Indicates whether oro not a synchronisation failure occurred")

GAEU_PWR_CCD_FEE_STATUS = Gauge("gaeu_pwr_ccd_fee_status", "Output status of PSU1 (V_CCD)")
GAEU_PWR_CLK_FEE_STATUS = Gauge("gaeu_pwr_clk_fee_status", "Output status of PSU2 (V_CLK)")
GAEU_PWR_AN1_FEE_STATUS = Gauge("gaeu_pwr_an1_fee_status", "Output status of PSU3 (V_AN1)")
GAEU_PWR_AN2_FEE_STATUS = Gauge("gaeu_pwr_an2_fee_status", "Output status of PSU4 (V_AN2)")
GAEU_PWR_AN3_FEE_STATUS = Gauge("gaeu_pwr_an3_fee_status", "Output status of PSU5 (V_AN3)")
GAEU_PWR_DIG_FEE_STATUS = Gauge("gaeu_pwr_dig_fee_status", "Output status of PSU6 (V_DIG)")

GAEU_CLK_PWR_50MHZ = Gauge("gaeu_clk_pwr_50mhz", "Indicates whether or not Clk_50MHz is enabled")
GAEU_CLK_PWR_CCDREAD = Gauge("gaeu_clk_pwr_ccdread", "Indicates whether or not Clk_ccdread is enabled")
GAEU_CLK_PWR_SVM = Gauge("gaeu_clk_pwr_svm", "Indicates whether or not Clk_heater is enabled")
GAEU_CLK_PWR_N_FFEE = Gauge("gaeu_clk_pwr_n_ffee", "Indicates whether or not Clk_50MHz or Clk_ccdread is enabled for "
                                                   "F-FEE nominal")
GAEU_CLK_PWR_R_FFEE = Gauge("gaeu_clk_pwr_r_ffee", "Indicates whether or not Clk_50MHz or Clk_ccdread is enabled for "
                                                   "F-FEE redundant")
GAEU_TESTPORT = Gauge("gaeu_testport", "Indicate whether or not the test port is active")

# N-CAM

GAEU_UVP_CCD_NFEE = Gauge("gaeu_uvp_ccd_nfee", "Camera Under-Voltage Protection (UVP) for V_CCD for the N-CAM [V]")
GAEU_OVP_CCD_NFEE = Gauge("gaeu_ovp_ccd_nfee", "Camera Over-Voltage Protection (OVP) for V_CCD for the N-CAM [V]")
GAEU_V_CCD_NFEE = Gauge("gaeu_v_ccd_nfee", "Camera voltage for V_CCD for the N-CAM [V]")
GAEU_OCP_CCD_NFEE = Gauge("gaeu_ocp_ccd_nfee", "Camera Over-Current Protection for V_CCD (OCP) for the N-CAM [A]")
GAEU_I_CCD_NFEE = Gauge("gaeu_i_ccd_nfee", "Camera current for V_CCD for the N-CAM [A]")

GAEU_UVP_CLK_NFEE = Gauge("gaeu_uvp_clk_nfee", "Camera Under-Voltage Protection (UVP) for V_CLK for the N-CAM [V]")
GAEU_OVP_CLK_NFEE = Gauge("gaeu_ovp_clk_nfee", "Camera Over-Voltage Protection (OVP) for V_CLK for the N-CAM [V]")
GAEU_V_CLK_NFEE = Gauge("gaeu_v_clk_nfee", "Camera voltage for V_CLK for the N-CAM [V]")
GAEU_OCP_CLK_NFEE = Gauge("gaeu_ocp_clk_nfee", "Camera Over-Current Protection for V_CLK (OCP) for the N-CAM [A]")
GAEU_I_CLK_NFEE = Gauge("gaeu_i_clk_nfee", "Camera current for V_CLK for the N-CAM [A]")

GAEU_UVP_AN1_NFEE = Gauge("gaeu_uvp_an1_nfee", "Camera Under-Voltage Protection (UVP) for V_AN1 for the N-CAM [V]")
GAEU_OVP_AN1_NFEE = Gauge("gaeu_ovp_an1_nfee", "Camera Over-Voltage Protection (OVP) for V_AN1 for the N-CAM [V]")
GAEU_V_AN1_NFEE = Gauge("gaeu_v_an1_nfee", "Camera voltage for V_AN1 for the N-CAM [V]")
GAEU_OCP_AN1_NFEE = Gauge("gaeu_ocp_an1_nfee", "Camera Over-Current Protection for V_AN1 (OCP) for the N-CAM [A]")
GAEU_I_AN1_NFEE = Gauge("gaeu_i_an1_nfee", "Camera current for V_AN1 for the N-CAM [A]")

GAEU_UVP_AN2_NFEE = Gauge("gaeu_uvp_an2_nfee", "Camera Under-Voltage Protection (UVP) for V_AN2 for the N-CAM [V]")
GAEU_OVP_AN2_NFEE = Gauge("gaeu_ovp_an2_nfee", "Camera Over-Voltage Protection (OVP) for V_AN2 for the N-CAM [V]")
GAEU_V_AN2_NFEE = Gauge("gaeu_v_an2_nfee", "Camera voltage for V_AN2 for the N-CAM [V]")
GAEU_OCP_AN2_NFEE = Gauge("gaeu_ocp_an2_nfee", "Camera Over-Current Protection for V_AN2 (OCP) for the N-CAM [A]")
GAEU_I_AN2_NFEE = Gauge("gaeu_i_an2_nfee", "Camera current for V_AN2 for the N-CAM [A]")

GAEU_UVP_AN3_NFEE = Gauge("gaeu_uvp_an3_nfee", "Camera Under-Voltage Protection (UVP) for V_AN3 for the N-CAM [V]")
GAEU_OVP_AN3_NFEE = Gauge("gaeu_ovp_an3_nfee", "Camera Over-Voltage Protection (OVP) for V_AN3 for the N-CAM [V]")
GAEU_V_AN3_NFEE = Gauge("gaeu_v_an3_nfee", "Camera voltage for V_AN3 for the N-CAM [V]")
GAEU_OCP_AN3_NFEE = Gauge("gaeu_ocp_an3_nfee", "Camera Over-Current Protection for V_AN3 (OCP) for the N-CAM [A]")
GAEU_I_AN3_NFEE = Gauge("gaeu_i_an3_nfee", "Camera current for V_AN3 for the N-CAM [A]")

GAEU_UVP_DIG_NFEE = Gauge("gaeu_uvp_dig_nfee", "Camera Under-Voltage Protection (UVP) for V_DIG for the N-CAM [V]")
GAEU_OVP_DIG_NFEE = Gauge("gaeu_ovp_dig_nfee", "Camera Over-Voltage Protection (OVP) for V_DIG for the N-CAM [V]")
GAEU_V_DIG_NFEE = Gauge("gaeu_v_dig_nfee", "Camera voltage for V_DIG for the N-CAM [V]")
GAEU_OCP_DIG_NFEE = Gauge("gaeu_ocp_dig_nfee", "Camera Over-Current Protection for V_DIG (OCP) for the N-CAM [A]")
GAEU_I_DIG_NFEE = Gauge("gaeu_i_dig_nfee", "Camera current for V_DIG for the N-CAM [A]")

# F-CAM

GAEU_UVP_CCD_FFEE = Gauge("gaeu_uvp_ccd_ffee", "Camera Under-Voltage Protection (UVP) for V_CCD for the F-CAM [V]")
GAEU_OVP_CCD_FFEE = Gauge("gaeu_ovp_ccd_ffee", "Camera Over-Voltage Protection (OVP) for V_CCD for the F-CAM [V]")
GAEU_V_CCD_FFEE = Gauge("gaeu_v_ccd_ffee", "Camera voltage for V_CCD for the F-CAM [V]")
GAEU_OCP_CCD_FFEE = Gauge("gaeu_ocp_ccd_ffee", "Camera Over-Current Protection for V_CCD (OCP) for the F-CAM [A]")
GAEU_I_CCD_FFEE = Gauge("gaeu_i_ccd_ffee", "Camera current for V_CCD for the F-CAM [A]")

GAEU_UVP_CLK_FFEE = Gauge("gaeu_uvp_clk_ffee", "Camera Under-Voltage Protection (UVP) for V_CLK for the F-CAM [V]")
GAEU_OVP_CLK_FFEE = Gauge("gaeu_ovp_clk_ffee", "Camera Over-Voltage Protection (OVP) for V_CLK for the F-CAM [V]")
GAEU_V_CLK_FFEE = Gauge("gaeu_v_clk_ffee", "Camera voltage for V_CLK for the F-CAM [V]")
GAEU_OCP_CLK_FFEE = Gauge("gaeu_ocp_clk_ffee", "Camera Over-Current Protection for V_CLK (OCP) for the F-CAM [A]")
GAEU_I_CLK_FFEE = Gauge("gaeu_i_clk_ffee", "Camera current for V_CLK for the F-CAM [A]")

GAEU_UVP_AN1_FFEE = Gauge("gaeu_uvp_an1_ffee", "Camera Under-Voltage Protection (UVP) for V_AN1 for the F-CAM [V]")
GAEU_OVP_AN1_FFEE = Gauge("gaeu_ovp_an1_ffee", "Camera Over-Voltage Protection (OVP) for V_AN1 for the F-CAM [V]")
GAEU_V_AN1_FFEE = Gauge("gaeu_v_an1_ffee", "Camera voltage for V_AN1 for the F-CAM [V]")
GAEU_OCP_AN1_FFEE = Gauge("gaeu_ocp_an1_ffee", "Camera Over-Current Protection for V_AN1 (OCP) for the F-CAM [A]")
GAEU_I_AN1_FFEE = Gauge("gaeu_i_an1_ffee", "Camera current for V_AN1 for the F-CAM [A]")

GAEU_UVP_AN2_FFEE = Gauge("gaeu_uvp_an2_ffee", "Camera Under-Voltage Protection (UVP) for V_AN2 for the F-CAM [V]")
GAEU_OVP_AN2_FFEE = Gauge("gaeu_ovp_an2_ffee", "Camera Over-Voltage Protection (OVP) for V_AN2 for the F-CAM [V]")
GAEU_V_AN2_FFEE = Gauge("gaeu_v_an2_ffee", "Camera voltage for V_AN2 for the F-CAM [V]")
GAEU_OCP_AN2_FFEE = Gauge("gaeu_ocp_an2_ffee", "Camera Over-Current Protection for V_AN2 (OCP) for the F-CAM [A]")
GAEU_I_AN2_FFEE = Gauge("gaeu_i_an2_ffee", "Camera current for V_AN2 for the F-CAM [A]")

GAEU_UVP_AN3_FFEE = Gauge("gaeu_uvp_an3_ffee", "Camera Under-Voltage Protection (UVP) for V_AN3 for the F-CAM [V]")
GAEU_OVP_AN3_FFEE = Gauge("gaeu_ovp_an3_ffee", "Camera Over-Voltage Protection (OVP) for V_AN3 for the F-CAM [V]")
GAEU_V_AN3_FFEE = Gauge("gaeu_v_an3_ffee", "Camera voltage for V_AN3 for the F-CAM [V]")
GAEU_OCP_AN3_FFEE = Gauge("gaeu_ocp_an3_ffee", "Camera Over-Current Protection for V_AN3 (OCP) for the F-CAM [A]")
GAEU_I_AN3_FFEE = Gauge("gaeu_i_an3_ffee", "Camera current for V_AN3 for the F-CAM [A]")

GAEU_UVP_DIG_FFEE = Gauge("gaeu_uvp_dig_ffee", "Camera Under-Voltage Protection (UVP) for V_DIG for the F-CAM [V]")
GAEU_OVP_DIG_FFEE = Gauge("gaeu_ovp_dig_ffee", "Camera Over-Voltage Protection (OVP) for V_DIG for the F-CAM [V]")
GAEU_V_DIG_FFEE = Gauge("gaeu_v_dig_ffee", "Camera voltage for V_DIG for the F-CAM [V]")
GAEU_OCP_DIG_FFEE = Gauge("gaeu_ocp_dig_ffee", "Camera Over-Current Protection for V_DIG (OCP) for the F-CAM [A]")
GAEU_I_DIG_FFEE = Gauge("gaeu_i_dig_ffee", "Camera current for V_DIG for the F-CAM [A]")

GAEU_EXT_CYCLE_TIME = Gauge("gaeu_ext_cycle_time", "External cycle time [s]")
