v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
N 60 -60 60 -40 {lab=0}
N 60 -60 350 -60 {lab=0}
N 60 -80 60 -60 {lab=0}
N 350 -70 350 -60 {lab=0}
N 350 -150 350 -130 {lab=v_cap}
N 60 -150 60 -140 {lab=v_in}
N 230 -150 350 -150 {lab=v_cap}
N 60 -150 170 -150 {lab=v_in}
N 430 -60 470 -60 {lab=0}
N 470 -70 470 -60 {lab=0}
N 430 -150 430 -120 {lab=v_cap}
N 350 -150 430 -150 {lab=v_cap}
N 430 -80 430 -60 {lab=0}
N 350 -60 430 -60 {lab=0}
N 470 -150 470 -130 {lab=v_out}
N 470 -150 530 -150 {lab=v_out}
C {gnd.sym} 60 -40 0 0 {name=l1 lab=0}
C {capa-2.sym} 350 -100 0 0 {name=C1
m=1
value=1e-12
device=polarized_capacitor}
C {lab_wire.sym} 340 -150 0 0 {name=p4 sig_type=std_logic lab=v_cap}
C {lab_wire.sym} 110 -150 0 0 {name=p1 sig_type=std_logic lab=v_in}
C {res.sym} 200 -150 3 0 {name=R1
value=1e6
footprint=1206
device=resistor
m=1}
C {vsource.sym} 60 -110 0 0 {name=V1 value="dc 1 ac 1" savecurrent=false}
C {vcvs.sym} 470 -100 0 0 {name=E1 value=10e4}
C {lab_wire.sym} 530 -150 0 0 {name=p2 sig_type=std_logic lab=v_out}
