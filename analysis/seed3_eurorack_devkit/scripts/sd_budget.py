"""SDMMC length/via budget: kit pad-to-pad path (from net_geometry geom.json) + Seed3 on-module length/vias
(Daisy_Seed3_datasheet.txt l.1803-1811 table) vs the datasheet guidelines (l.1795-1798): max difference < 10 mm,
max length < 120 mm, equal via count on DATA and CMD."""
import sys, json
g=json.load(open(sys.argv[1]))
# Seed3 module internal: HW pin -> (length mm, vias)  [datasheet Table, p.33]
seed={'SDMMC_CK':(4.853,0),'SDMMC_CMD':(9.767,1),'SDMMC_D0':(13.94,2),'SDMMC_D1':(14.942,2),'SDMMC_D2':(14.224,1),'SDMMC_D3':(17.586,1)}
seedpin={'SDMMC_CK':'A1.7','SDMMC_CMD':'A1.6','SDMMC_D0':'A1.5','SDMMC_D1':'A1.4','SDMMC_D2':'A1.3','SDMMC_D3':'A1.2'}
sock={'SDMMC_CK':'U7.5','SDMMC_CMD':'U7.3','SDMMC_D0':'U7.7','SDMMC_D1':'U7.8','SDMMC_D2':'U7.1','SDMMC_D3':'U7.2'}
rows=[]
for n,(sl,sv) in seed.items():
    o=g[n]; a,b=seedpin[n],sock[n]
    L=o['paths'].get(f"{a}<->{b}") or o['paths'].get(f"{b}<->{a}")
    rows.append((n,L,o['vias'],sl,sv,L+sl,o['vias']+sv))
    print(f"{n:<10} kit {L:>5.1f} mm / {o['vias']} via   seed {sl:>6.3f} mm / {sv} via   total {L+sl:>5.1f} mm / {o['vias']+sv} via")
tot=[r[5] for r in rows]; print(f"max total {max(tot):.1f} mm (<120 ok={max(tot)<120}); max diff {max(tot)-min(tot):.1f} mm (<10 ok={max(tot)-min(tot)<10})")
dat=[r for r in rows if r[0]!='SDMMC_CK']; print("DATA+CMD total vias:",{r[0]:r[6] for r in dat}, "equal =",len({r[6] for r in dat})==1)
