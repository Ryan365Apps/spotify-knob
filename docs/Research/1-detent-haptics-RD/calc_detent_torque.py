#!/usr/bin/env python3
"""
Magnetic detent physics for "the 60" by Cadrane — strand B calculation script.

Geometry (settled design, docs/CAD-BRIEF.md):
  - 60 steel poles (M2.5 grub screws, Ø2.5 mm) threaded radially into the rotating
    knob's inner wall, pole-tip pitch circle Ø122.8 mm (r = 61.4 mm), pitch 6.4 mm,
    at height z = 15 mm.
  - 6 N42 neodymium block magnets, 3 x 6 x 3 mm, on a stationary carrier inside the
    knob, magnetised radially outward, radial air gap ~0.8 mm to the pole tips.
  - Carrier can drop 3 mm axially to weaken the detent.

Model:
  The permanent magnet field is computed numerically with magpylib (analytical
  cuboid solution, exact for the magnet alone). The steel pole is a soft magnetic
  body; magpylib cannot model induced magnetisation, so the pole is discretised
  into ~0.25 mm cells and each cell is treated as an induced dipole with a
  mean-field (demagnetising-factor) closure:

      M_cell = min( B_applied / (mu0 * N_D),  M_sat )      [A/m]

  where N_D is the axial demagnetising factor of the whole pole cylinder
  (L/D = 1.6 -> N_D ~ 0.25, estimate from standard cylinder demag tables,
  e.g. Coey, "Magnetism and Magnetic Materials", CUP 2010, table 2.2) and
  mu0*M_sat = 2.0 T for low-carbon steel (estimate; pure iron 2.15 T).

  Interaction energy per cell (continuous across saturation):
      unsaturated: u = -1/2 * M * B * V
      saturated:   u = -(M_sat*B - 1/2*mu0*N_D*M_sat^2) * V
  Tangential force = -dU/dy (numerical gradient over offset sweep).
  Radial force     = -dU/dgap (finite difference).

  Cross-check: Maxwell-stress / flux-capture estimate
      F_r ~ (k_img * B_face_avg)^2 * A_pole / (2*mu0),  k_img ~ 1.8 (1.6..2.0)
  where B_face_avg is the free-space field averaged over the pole face disc and
  k_img accounts for the flux concentration by the iron (image effect).

  Expected error band of the mean-field model vs a proper finite-element
  solution: roughly -40 % / +60 % (it ignores cell-cell interaction, thread
  geometry, and knob-wall material). Treated as an ESTIMATE throughout; a bench
  measurement (strand-A rig) is the arbiter.

Units: SI internally (m, T, N). Printed in mm / N / mNm.
Run:  python calc_detent_torque.py            (takes ~1-2 min)
"""

import numpy as np
import magpylib as magpy

MU0 = 4e-7 * np.pi

# ---------------------------------------------------------------- geometry ---
R_POLE_TIP = 61.4e-3        # m, pole tip pitch-circle radius (Ø122.8 mm)
PITCH = 6.4e-3              # m, tangential pole pitch (2*pi*61.4/60 = 6.43 mm)
GAP0 = 0.8e-3               # m, nominal radial air gap
POLE_D = 2.5e-3             # m, grub screw nominal Ø (threads ignored, see doc)
POLE_L = 4.0e-3             # m, assumed engaged magnetic length (estimate)
MSAT_B = 2.0                # T, mu0*Ms for low-carbon steel (estimate)
N_DEMAG = 0.25              # cylinder L/D=1.6 axial demag factor (estimate)

# Br by grade — K&J Magnetics grade table, https://www.kjmagnetics.com/specs.asp
BR = {"N35": 1.21, "N42": 1.30, "N52": 1.45}

CELL = 0.25e-3              # pole discretisation step


def pole_cells(diam=POLE_D, length=POLE_L, step=CELL):
    """Cell centres of the pole cylinder, tip at x=0, axis +x (radially out)."""
    r = diam / 2
    xs = np.arange(step / 2, length, step)
    yz = np.arange(-r + step / 2, r, step)
    Y, Z = np.meshgrid(yz, yz, indexing="ij")
    mask = Y**2 + Z**2 <= r**2
    y, z = Y[mask], Z[mask]
    pts = np.array([(xi, yi, zi) for xi in xs for yi, zi in zip(y, z)])
    vol = step**3
    return pts, vol


def magnet(Br, dims_rad_tan_ax):
    """Cuboid magnet, outer (north) face at x=0, magnetised +x (outward)."""
    dr, dt, da = dims_rad_tan_ax
    return magpy.magnet.Cuboid(
        polarization=(Br, 0, 0),
        dimension=(dr, dt, da),
        position=(-dr / 2, 0, 0),
    )


def energy(mag, cells, vol, msat_b=MSAT_B, ndem=N_DEMAG):
    """Interaction energy of the soft pole (cells: N x 3) with the magnet."""
    B = mag.getB(cells)
    Bmag = np.linalg.norm(B, axis=1)
    Bstar = ndem * msat_b                    # saturation knee in applied B
    Ms = msat_b / MU0
    u = np.where(
        Bmag < Bstar,
        -0.5 * Bmag**2 / (MU0 * ndem),                     # linear regime
        -(Ms * Bmag - 0.5 * ndem * MU0 * Ms**2),           # saturated
    )
    return u.sum() * vol


def profile(Br=BR["N42"], dims=(3e-3, 3e-3, 6e-3), gap=GAP0, z_off=0.0,
            pole_d=POLE_D, pole_l=POLE_L, ndem=N_DEMAG, msat_b=MSAT_B,
            n_side=1, ny=65):
    """Energy and tangential force vs tangential offset (3 poles tracked)."""
    mag = magnet(Br, dims)
    base, vol = pole_cells(pole_d, pole_l)
    offs = np.linspace(-PITCH / 2, PITCH / 2, ny)
    U = np.zeros(ny)
    for i, yo in enumerate(offs):
        for k in range(-n_side, n_side + 1):
            c = base + np.array([gap, yo + k * PITCH, z_off])
            U[i] += energy(mag, c, vol, msat_b, ndem)
    Ft = -np.gradient(U, offs)               # N, tangential force on the poles
    return offs, U, Ft


def radial_force(Br=BR["N42"], dims=(3e-3, 3e-3, 6e-3), gap=GAP0, z_off=0.0,
                 dg=0.02e-3):
    mag = magnet(Br, dims)
    base, vol = pole_cells()
    Um = energy(mag, base + np.array([gap - dg, 0, z_off]), vol)
    Up = energy(mag, base + np.array([gap + dg, 0, z_off]), vol)
    return -(Up - Um) / (2 * dg)             # N, + toward magnet


def maxwell_crosscheck(Br=BR["N42"], dims=(3e-3, 3e-3, 6e-3), gap=GAP0,
                       k_img=1.8):
    """Flux-capture / Maxwell-stress estimate of radial pull on the pole."""
    mag = magnet(Br, dims)
    r = POLE_D / 2
    th = np.linspace(0, 2 * np.pi, 24, endpoint=False)
    rr = np.linspace(0, r, 8)
    pts = np.array([(gap, ri * np.cos(t), ri * np.sin(t))
                    for ri in rr for t in th])
    Bx = mag.getB(pts)[:, 0]
    Bavg = np.average(np.abs(Bx), weights=np.repeat(rr, len(th)))
    A = np.pi * r**2
    return (k_img * Bavg)**2 * A / (2 * MU0), Bavg


def peak_torque(Ft, r_torque=R_POLE_TIP):
    """Peak detent torque, six magnets in phase, N -> mNm."""
    return 6 * np.max(np.abs(Ft)) * r_torque * 1e3


def run():
    print("=" * 72)
    print("BASELINE  N42 3x6x3 (3 rad x 3 tan x 6 ax), gap 0.8 mm")
    print("=" * 72)
    offs, U, Ft = profile()
    ipk = np.argmax(np.abs(Ft))
    Fr = radial_force()
    Fmx, Bavg = maxwell_crosscheck()
    print(f"free-space |Bx| avg over pole face @0.8mm : {Bavg:.3f} T")
    print(f"radial pull per magnet (dipole model)     : {Fr:.3f} N")
    print(f"radial pull per magnet (Maxwell k=1.8)    : {Fmx:.3f} N")
    print(f"peak tangential force per magnet          : {np.max(np.abs(Ft)):.3f} N"
          f"  at offset {abs(offs[ipk])*1e3:.2f} mm")
    print(f"peak detent torque (6 magnets, r=61.4mm)  : {peak_torque(Ft):.1f} mNm")
    k_lin = -np.gradient(Ft, offs)[len(offs) // 2]          # N/m per magnet
    k_ang = 6 * k_lin * R_POLE_TIP**2                        # Nm/rad
    print(f"angular stiffness at detent centre        : {k_ang*1e3:.1f} mNm/rad "
          f"({k_ang*np.pi/180*1e3:.2f} mNm/deg)")

    print("\nDetent profile (offset mm -> Ft per magnet N, torque 6x mNm):")
    for i in range(0, len(offs), 4):
        print(f"  {offs[i]*1e3:+6.2f}  {Ft[i]:+7.3f}  "
              f"{6*Ft[i]*R_POLE_TIP*1e3:+8.1f}")

    print("\n" + "=" * 72)
    print("MAGNET ORIENTATION  (6 mm axial vs 6 mm tangential)")
    print("=" * 72)
    for name, dims in [("3r x 3t x 6a (tall, baseline)", (3e-3, 3e-3, 6e-3)),
                       ("3r x 6t x 3a (wide)",           (3e-3, 6e-3, 3e-3))]:
        _, _, F = profile(dims=dims)
        print(f"  {name:34s} peak torque {peak_torque(F):6.1f} mNm")

    print("\n" + "=" * 72)
    print("GAP SENSITIVITY  (N42 3x6x3 tall)")
    print("=" * 72)
    for g in [0.4e-3, 0.8e-3, 1.2e-3, 2.0e-3]:
        _, _, F = profile(gap=g)
        print(f"  gap {g*1e3:.1f} mm : peak torque {peak_torque(F):6.1f} mNm "
              f"(peak Ft {np.max(np.abs(F)):.3f} N/magnet)")

    print("\n" + "=" * 72)
    print("GRADE SENSITIVITY  (3x6x3 tall, gap 0.8 mm)")
    print("=" * 72)
    for gname, br in BR.items():
        _, _, F = profile(Br=br)
        print(f"  {gname} (Br {br:.2f} T): peak torque {peak_torque(F):6.1f} mNm")

    print("\n" + "=" * 72)
    print("SIZE SENSITIVITY  (N42, gap 0.8 mm; dims radial x tang x axial)")
    print("=" * 72)
    sizes = [("3 x 3 x 6 (baseline)", (3e-3, 3e-3, 6e-3)),
             ("3 x 4 x 6",           (3e-3, 4e-3, 6e-3)),
             ("4 x 3 x 6  [4 mm radial > 3.5 mm annulus]", (4e-3, 3e-3, 6e-3)),
             ("3 x 3 x 8",           (3e-3, 3e-3, 8e-3)),
             ("3.5 x 4 x 8 (max-in-annulus)", (3.5e-3, 4e-3, 8e-3)),
             ("5 x 5 x 5  [violates annulus + pitch]", (5e-3, 5e-3, 5e-3))]
    for name, d in sizes:
        _, _, F = profile(dims=d)
        print(f"  {name:44s} peak torque {peak_torque(F):6.1f} mNm")

    print("\n" + "=" * 72)
    print("N52 UPGRADE PATHS  (gap 0.8 mm)")
    print("=" * 72)
    for name, br, d in [("N52 3 x 3 x 6", BR['N52'], (3e-3, 3e-3, 6e-3)),
                        ("N52 3.5 x 4 x 8", BR['N52'], (3.5e-3, 4e-3, 8e-3))]:
        _, _, F = profile(Br=br, dims=d)
        print(f"  {name:20s} peak torque {peak_torque(F):6.1f} mNm")

    print("\n" + "=" * 72)
    print("VERTICAL FADE  (carrier dropped, N42 3x6x3 tall, gap 0.8 mm)")
    print("=" * 72)
    _, _, F0 = profile(z_off=0.0)
    T0 = peak_torque(F0)
    for zo in [0.0, 1e-3, 2e-3, 3e-3, 4.5e-3, 6e-3]:
        _, _, F = profile(z_off=zo)
        T = peak_torque(F)
        print(f"  z-offset {zo*1e3:3.1f} mm : peak torque {T:6.1f} mNm "
              f"({100*T/T0:5.1f} % of engaged)")

    print("\n" + "=" * 72)
    print("MODEL SENSITIVITY  (demag factor and pole length, baseline)")
    print("=" * 72)
    for nd in [0.15, 0.25, 0.35]:
        _, _, F = profile(ndem=nd)
        print(f"  N_demag {nd:.2f} : peak torque {peak_torque(F):6.1f} mNm")
    for pl in [3e-3, 4e-3, 5e-3]:
        _, _, F = profile(pole_l=pl)
        print(f"  pole length {pl*1e3:.0f} mm : peak torque {peak_torque(F):6.1f} mNm")
    for pd, pl in [(2.0e-3, 4e-3), (2.5e-3, 4e-3), (3.0e-3, 4e-3)]:
        _, _, F = profile(pole_d=pd, pole_l=pl)
        print(f"  pole Ø {pd*1e3:.1f} mm : peak torque {peak_torque(F):6.1f} mNm")

    print("\n" + "=" * 72)
    print("HYSTERESIS DRAG ESTIMATE (analytic)")
    print("=" * 72)
    Vp = np.pi * (POLE_D / 2)**2 * POLE_L
    for name, Hc in [("annealed low-C steel", 150.0),
                     ("cold-drawn mild steel", 400.0),
                     ("hardened alloy (grub screw 45H)", 2500.0)]:
        Bpk = 1.0   # T, typical peak flux in pole body during a pass (from model)
        w = 4 * Hc * Bpk                       # J/m^3 per full cycle (rough)
        E_step = 6 * w * Vp                    # 6 magnets engage per step
        T_drag = E_step / (2 * np.pi / 60)     # J / rad over one 6-deg step
        print(f"  {name:34s} Hc~{Hc:5.0f} A/m -> drag ~{T_drag*1e3:5.2f} mNm")


if __name__ == "__main__":
    run()
