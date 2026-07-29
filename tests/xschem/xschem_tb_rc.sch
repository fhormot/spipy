v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
N 90 -60 90 -40 {lab=0}
N 90 -60 380 -60 {lab=0}
N 90 -80 90 -60 {lab=0}
N 380 -70 380 -60 {lab=0}
N 380 -150 380 -130 {lab=v_cap}
N 90 -150 90 -140 {lab=v_in}
N 260 -150 380 -150 {lab=v_cap}
N 90 -150 200 -150 {lab=v_in}
C {devices/vsource.sym} 90 -110 0 0 {name=Vin value="pulse (0 1.5 100n 0.5n 0.5n 200n 2)"}
C {gnd.sym} 90 -40 0 0 {name=l1 lab=0}
C {capa-2.sym} 380 -100 0 0 {name=C1
m=1
value=1e-12
device=polarized_capacitor}
C {lab_wire.sym} 370 -150 0 0 {name=p4 sig_type=std_logic lab=v_cap}
C {lab_wire.sym} 140 -150 0 0 {name=p1 sig_type=std_logic lab=v_in}
C {res.sym} 230 -150 3 0 {name=R1
value=1e6
footprint=1206
device=resistor
m=1}
