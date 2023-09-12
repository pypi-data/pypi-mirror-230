from wetb.gtsdf import gtsdf
import matplotlib.pyplot as plt
import numpy as np
from numpy import newaxis as na
import pytest
from h2lib._h2lib import H2Lib, MultiH2Lib
from numpy import testing as npt
from h2lib.tests.test_files import tfp
from wetb.hawc2.htc_file import HTCFile
import time
from tqdm import tqdm


def test_echo_version():
    with H2Lib() as h2:
        h2.suppress_output = False
        h2.echo_version()
        h2.suppress_output = True


def test_sensors():
    with H2Lib() as h2:
        model_path = tfp + "minimal/"
        htc = HTCFile(model_path + 'htc/minimal.htc')
        htc.output.add_sensor("general", 'variable', [1, 5, 'mysensor', 'myunit', 'mydesc'])
        htc.set_name('tmp')
        htc.save()
        h2.read_input('htc/tmp.htc', model_path)
        i1 = h2.add_sensor('wind free_wind 1 0 0 -119;')  # adds three sensors
        assert i1 == 3
        i2 = h2.add_sensor('general step 0.5 1 2;')
        assert i2 == 4
        i3 = h2.add_sensor('general variable 1 5 myname myunit mydesc;')
        assert i3 == 5
        h2.init()
        t = h2.step()
        assert h2.get_sensor_info(1) == ['WSP gl. coo.,Vx', 'm/s',
                                         'Free wind speed Vx, gl. coo, of gl. pos    0.00,   0.00,-119.00']
        assert h2.get_sensor_info(2) == ['WSP gl. coo.,Vy', 'm/s',
                                         'Free wind speed Vy, gl. coo, of gl. pos    0.00,   0.00,-119.00']
        assert h2.get_sensor_info(3) == ['WSP gl. coo.,Vz', 'm/s',
                                         'Free wind speed Vz, gl. coo, of gl. pos    0.00,   0.00,-119.00']
        assert h2.get_sensor_info(4) == ['Step', '-', 'Step value']
        assert h2.get_sensor_info(5) == ['myname', 'myunit', 'mydesc']

        r = []
        for _ in range(10):
            r.append([t, h2.get_sensor_value(4), h2.get_sensor_value(5)])
            if t == 0.6:
                h2.set_variable_sensor_value(1, 2)
            t = h2.step()
        r = np.array(r)
        npt.assert_array_equal(r[:, 1], np.where(r[:, 0] <= .5, 1, 2))
        npt.assert_array_equal(r[:, 2], np.where(r[:, 0] >= .7, 2, 5.))
        time, data, _ = gtsdf.load(h2.model_path + 'res/tmp.hdf5')
        npt.assert_array_equal(data[:, 0], np.where(time >= .7, 2, 5.))


def test_set_windspeed_uvw():
    with H2Lib() as h2:
        pos = [0, 0, -119]
        model_path = tfp + "minimal/"
        h2.read_input('htc/minimal.htc', model_path)
        Nxyz = [8, 4, 2]
        h2.init_windfield(Nxyz, dxyz=[1., 1, 1], box_offset_yz=[0., -119])
        h2.init()
        u, v, w = 1, 2, 3
        uvw = np.zeros([3] + Nxyz) + np.array([u, v, w])[:, na, na, na]
        h2.set_windfield(uvw, 0)
        vx, vy, vz = h2.get_wind_speed(pos)
        assert vx == v
        assert vy == u
        assert vz == -w
        npt.assert_array_equal([u, v, w], h2.get_uvw(pos))


def test_set_windspeed_interpolation():
    with H2Lib() as h2:
        model_path = tfp + "minimal/"
        h2.read_input('htc/minimal.htc', model_path)
        Nxyz = np.array([8, 4, 2])
        h2.init_windfield(Nxyz, dxyz=[2., 3, 4], box_offset_yz=[-4.5, 117])
        h2.init()
        uvw = np.array(np.meshgrid(np.arange(Nxyz[0]) + 100, np.arange(Nxyz[1]) + 200, np.arange(Nxyz[2]) + 300,
                                   indexing='ij'),
                       dtype=np.float64)
        h2.set_windfield(uvw, 0)

        # test u
        y = np.linspace(0, 14, 10)
        np.testing.assert_array_almost_equal([h2.get_wind_speed([0, y_, 0])[1] for y_ in y], np.linspace(100, 107, 10))

        h2.set_windfield(uvw, -5.)
        # box moved -6m offset
        np.testing.assert_array_almost_equal([h2.get_wind_speed([0, y_, 0])[1]
                                             for y_ in y - 5], np.linspace(100, 107, 10))

        h2.run(3)
        # box moved 3s * 5m/s - 5m offset = 10
        np.testing.assert_array_almost_equal([h2.get_wind_speed([0, y_, 0])[1]
                                             for y_ in y + 10], np.linspace(100, 107, 10))

        h2.set_windfield(uvw, -5.)
        # box moved 6m offset
        np.testing.assert_array_almost_equal([h2.get_wind_speed([0, y_, 0])[1]
                                             for y_ in y - 5], np.linspace(100, 107, 10))

        # test v
        x = np.linspace(-4.5, 4.5, 10)
        np.testing.assert_array_almost_equal([h2.get_wind_speed([x_, 0, 0])[0] for x_ in x], np.linspace(200, 203, 10))

        # test w
        z = np.linspace(-117, -121, 10)
        np.testing.assert_array_almost_equal([h2.get_wind_speed([0, 0, z_])[2] for z_ in z], -np.linspace(300, 301, 10))


def test_mann_turb():
    with H2Lib() as h2:
        U = 5
        from hipersim import MannTurbulenceField
        mtf = MannTurbulenceField.from_hawc2(filenames=[tfp + f'minimal/turb/hawc2_mann_l33.6_ae0.1000_g3.9_h0_512xd32xd16_2.000x3.00x4.00_s0001_{uvw}' for uvw in 'uvw'],
                                             alphaepsilon=.1, L=33.6, Gamma=3.9,
                                             Nxyz=(512, 32, 16), dxyz=(2, 3, 4), seed=1, HighFreqComp=0)

        time, data, _ = gtsdf.load(tfp + 'minimal/res/minimal_mann_turb.hdf5')
        time, data = time[1000:], data[1000:]
        vx, vy, vz = data.T
        h2_uvw = [vy, vx, -vz]
        model_path = tfp + "minimal/"
        h2.read_input('htc/minimal.htc', model_path)
        h2.init_windfield(Nxyz=mtf.Nxyz, dxyz=mtf.dxyz, box_offset_yz=[0, 0])
        h2.init()
        h2.set_windfield(uvw=mtf.uvw.astype(np.float64), box_offset_x=-(mtf.Nx - 1) * mtf.dx)
        h2l_vxyz = []
        for t in tqdm(time, disable=0):
            h2.run(t)
            h2l_vxyz.append(h2.get_wind_speed([0, 0, 0]))
        vx, vy, vz = np.array(h2l_vxyz).T
        h2l_uvw = [vy, vx, -vz]

        x = (mtf.Nx * mtf.dx) - U * time - 2
        mtf_uvw = mtf(x, x * 0, x * 0).T

        if 0:
            plt.plot(time, h2_uvw[0], label='h2')
            plt.plot(time, mtf_uvw[0], label='mtf')
            plt.plot(time, h2l_uvw[0], label='h2l')
            plt.legend()
            plt.show()

        npt.assert_array_almost_equal(mtf_uvw, h2_uvw)
        npt.assert_array_almost_equal(mtf_uvw, h2l_uvw)


def test_mann_turb_small_buffer():
    with H2Lib() as h2:
        from hipersim import MannTurbulenceField
        U = 5
        mtf = MannTurbulenceField.from_hawc2(filenames=[tfp + f'minimal/turb/hawc2_mann_l33.6_ae0.1000_g3.9_h0_512xd32xd16_2.000x3.00x4.00_s0001_{uvw}' for uvw in 'uvw'],
                                             alphaepsilon=.1, L=33.6, Gamma=3.9,
                                             Nxyz=(512, 32, 16), dxyz=(2, 3, 4), seed=1, HighFreqComp=0)

        time, data, _ = gtsdf.load(tfp + 'minimal/res/minimal_mann_turb.hdf5')
        time, data = time[:1400], data[:1400]
        vx, vy, vz = data.T
        h2_uvw = [vy, vx, -vz]
        model_path = tfp + "minimal/"
        h2.read_input('htc/minimal.htc', model_path)
        h2.init_windfield(Nxyz=(128, 32, 16), dxyz=mtf.dxyz, box_offset_yz=[0, 0])
        h2.init()
        h2l_vxyz = []
        h2.set_windfield(uvw=mtf.uvw[:, -128:].astype(np.float64), box_offset_x=-(mtf.Nx - 1) * mtf.dx)
        for t in tqdm(time):
            t = np.round(t, 6)
            h2.run(t)
            if t % 40 == 0:
                i = int(512 - 128 - t * U / 2)
                h2.set_windfield(uvw=mtf.uvw[:, i:i + 128].astype(np.float64), box_offset_x=-(mtf.Nx - 1) * mtf.dx)
            h2l_vxyz.append(h2.get_wind_speed([0, 0, 0]))
        vx, vy, vz = np.array(h2l_vxyz).T
        h2l_uvw = [vy, vx, -vz]

        x = ((mtf.Nx - 1) * mtf.dx) - U * time
        mtf_uvw = mtf(x, x * 0, x * 0).T

        if 0:
            plt.plot(time, h2_uvw[0], '-', label='h2')
            plt.plot(time, mtf_uvw[0], '--', label='mtf')
            plt.plot(time, h2l_uvw[0], '-', label='h2l')
            plt.legend()
            plt.show()

        npt.assert_array_almost_equal(mtf_uvw, h2_uvw)
        npt.assert_array_almost_equal(mtf_uvw, h2l_uvw)


def test_parallel():
    N = 3
    mh2 = MultiH2Lib(N)
    assert mh2.getState() == [0, 0, 0]
    mh2.setState([4, 5, 6])
    assert mh2.getState() == [4, 5, 6]
    mh2.close()


def test_parallel_context_manager():
    N = 3
    with MultiH2Lib(N) as mh2:
        mh2.init_windfield(Nxyz=(128, 32, 16), dxyz=[(1, 2, 3), (4, 5, 6), (7, 8, 9)], box_offset_yz=[0, 0])
        assert mh2.getState() == [0, 0, 0]
        mh2.setState([4, 5, 6])
        assert mh2.getState() == [4, 5, 6]
        mh2[0].setState(10)
        assert mh2.getState() == [10, 5, 6]
        t = time.time()
        mh2.work(2)
        assert time.time() - t < 2.5
