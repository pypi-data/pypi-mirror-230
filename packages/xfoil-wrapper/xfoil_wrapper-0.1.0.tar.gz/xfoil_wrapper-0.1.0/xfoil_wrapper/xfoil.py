import os, subprocess as sp, shutil, matplotlib.pyplot as plt
import numpy as np, random, string
from typing import Union, Iterable
from importlib.resources import files
from .utils import read_polar_file, read_cp_file, read_cf_file


_EXE_LOCATION = "xfoil_wrapper.__exe__"
XF_KWARGS = {"ncrit": 9.0, "xtr": (1.0, 1.0), "iter": 100, "timeout": 15}


def get_xfoil_exe():
    """
    To load the xfoil executable file.
    """
    exe_file = files(_EXE_LOCATION).joinpath("xfoil.exe")
    return exe_file


class XFoil:
    def __init__(
        self,
        airfoil: Union[str, os.PathLike, np.ndarray],
        airfoil_name: Union[str, None] = None,
        repanel: bool = True,
        hide_plot: bool = True,
        root: Union[str, os.PathLike, None] = None,
        ignore_error: bool = True,
        **xf_kwargs
    ):
        """
        interface to XFOIL 6.99 (Marc Drela, MIT).

        args:
            airfoil: can be the airfoil filepath or coordinates [Nx2] array.
            airfoil_name: name of the airfoil.
            repanel: action for repaneling airfoil coordinates to the default
            160 points.
            hide_plot: hide XFOIL plot?
            root: working directory of Xfoil. if None, it will be temporary.
            ignore_error: when it is set to True and errors occur, any warning is
            ignored.
            xf_kwargs: keyword arguments for running xfoil.
        """
        self.repanel = repanel
        self.hide_plot = hide_plot

        if type(airfoil) in [str, os.PathLike]:
            with open(airfoil, "r") as f:
                line0 = f.readlines()[0].strip()
                try:
                    coord = [float(x) for x in line0.split()]
                except ValueError:
                    foil_name = line0
            f.close()
        else:
            if airfoil_name is None:
                foil_name = "airfoil"
            else:
                foil_name = airfoil_name
        self.airfoil_name = foil_name

        self.__exe__ = get_xfoil_exe()

        if root is None:
            wdir = "".join(
                random.choice(
                    string.ascii_uppercase + string.ascii_lowercase + string.digits
                )
                for _ in range(8)
            )
            self.wdir = os.path.join(".", wdir)
            self.__clean__ = True
        else:
            self.wdir = os.path.join(root, self.airfoil_name)
            self.__clean__ = False
        if not os.path.isdir(self.wdir):
            os.makedirs(self.wdir)

        if type(airfoil) is np.ndarray:
            self.airfoil_path = os.path.join(self.wdir, "%s.dat" % self.airfoil_name)
            np.savetxt(self.airfoil_path, airfoil, header=self.airfoil_name)
        else:
            self.airfoil_path = airfoil

        self.ignore_error = ignore_error
        self.xf_kwargs = XF_KWARGS.copy()
        self.xf_kwargs.update(xf_kwargs)

        self.data = {}

    def _default_coms(self, re: float, mach: float):
        """
        return a list containing keystorkes for communicating XFOIL
        """
        coms = ["name", self.airfoil_name]

        if self.hide_plot:
            coms.extend(["pcop", "plop", "g,F", ""])

        if self.repanel:
            coms.append("pane")

        oper = [
            "oper",
            "iter %s" % self.xf_kwargs["iter"],
            "re %s" % re,
            "mach %s" % mach,
            "visc",
        ]
        vpar = [
            "vpar",
            "xtr %s %s" % self.xf_kwargs["xtr"],
            "n %s" % self.xf_kwargs["ncrit"],
            "",
        ]
        coms.extend(oper + vpar)

        return coms

    def _run_xfoil(self, cmd: Iterable[str], out_dir: Union[str, os.PathLike]):
        """
        executing XFOIL with the main commands specified in 'cmd'.
        """

        # Executing XFOIL process
        try:
            with open(os.path.join(out_dir, "log.dat"), "w") as log:
                proc = sp.Popen(
                    [self.__exe__, self.airfoil_path],
                    stdin=sp.PIPE,
                    stdout=log,
                    stderr=sp.STDOUT,
                    text=True,
                )
                proc.communicate("\n".join(cmd), timeout=self.xf_kwargs["timeout"])
            log.close()

        except sp.TimeoutExpired:
            proc.kill()
            if not self.ignore_error:
                raise RuntimeError(
                    "XFoil run timed out!\n"
                    'If this was not expected, try pass keyword argument "timeout" with value greater than 30.'
                )

        except sp.CalledProcessError as e:
            if not self.ignore_error:
                if e.returncode == 11:
                    raise RuntimeError(
                        "XFoil segmentation-faulted. This is likely because the airfoil has too many points.\n"
                        "Try repaneling your airfoil by setting repanel to True when creating XFoil instance.\n"
                        "For further debugging, turn on the verbose flag"
                    )
                elif e.returncode == 8 or e.returncode == 136:
                    raise RuntimeError(
                        "XFoil returned a floating point exception. This is probably because you are trying to start\n"
                        "your analysis at an operating point where the viscous boundary layer cant be initialized based\n"
                        "on the computed inviscid flow. (You are probably hitting a Goldstein singularity.) Try starting\n"
                        "your XFoil run at a less-aggressive (alpha closer to 0, higher Re) operating point."
                    )
                else:
                    raise e
            else:
                pass

    def run_alphas(
        self,
        alphas: Iterable[float],
        re: Union[Iterable[float], float] = 1e6,
        mach: float = 0.0,
        get_sectload: bool = False,
    ):
        """
        run XFOIL for a set of angle of attacks. update and return XFoil.data attribute which
         is a dictionary {'polar': polar_data, 'cp': cp_data, 'cf': cf_data,
                          'coord': airfoil_coordinate}

        args:
            alphas: iterable of alphas in deg unit.

            re: Reynolds number(s).

            mach: Mach number of the simulation.

            get_sectload: set it to True to print the Cp and Cf data of each alpha. filepaths will be
            in out_dir/airfoil_name directory and has name alpha*.cp and alpha*.cf where * indicates
            each alpha.
        """

        if type(re) is float:
            res = [re]
        else:
            res = list(re)

        datas = []
        # iterate process for re
        for re in res:
            wdir = os.path.join(self.wdir, "Ma %s Re %d" % (mach, re))
            if not os.path.isdir(wdir):
                os.makedirs(wdir)

            # Assort Xfoil commands
            polar_filename = os.path.join(wdir, "polar.dat")
            if os.path.isfile(polar_filename):
                os.remove(polar_filename)

            cp_files, cf_files = [], []
            cmd = self._default_coms(re, mach) + ["pacc", polar_filename, ""]
            for a in alphas:
                cmd.append("alfa %s" % a)

                if get_sectload:
                    cp_filename = os.path.join(wdir, "alpha%s.cp" % (a))
                    cp_files.append(cp_filename)
                    cmd.extend(["cpwr", cp_filename])

                    cf_filename = os.path.join(wdir, "alpha%s.cf" % (a))
                    cf_files.append(cf_filename)
                    cmd.extend(["vplo", "cf", "dump", cf_filename, ""])

            cmd += ["pacc", "", "quit"]

            # Run Xfoil
            self._run_xfoil(cmd, wdir)

            # Colelct Data
            data = {"mach": mach, "re": re, "cp": [], "cf": []}
            data["polar"] = read_polar_file(polar_filename)

            for cp_name, cf_name in tuple(zip(cp_files, cf_files)):
                cp_data = read_cp_file(cp_name)
                cf_data = read_cf_file(cf_name)
                data["cp"].append(cp_data)
                data["cf"].append(cf_data)

            datas.append(data)

        # clean tree if not in debug mode
        if self.__clean__:
            shutil.rmtree(self.wdir)
        self.data = datas

        return datas

    def plot_polars(self):
        """
        plot recent polar data.
        """

        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=[16, 9])

        for data in self.data:
            re = "Re %d" % data["re"]
            polar = data["polar"]
            ax1.plot(polar["alpha"], polar["CL"], label=re)
            ax2.plot(polar["CL"], polar["CD"], label=re)
            ax3.plot(polar["alpha"], polar["CM"], label=re)
            ax4.plot(polar["alpha"], polar["CL"] / polar["CD"], label=re)

        xlabels = ["alpha [deg]"] * 3 + ["CL"]
        ylabels = [r"$c_{L}$", r"$c_{M}$", r"$c_{L}/c_{D}$", r"$c_{D}$"]
        for i, ax in enumerate([ax1, ax3, ax4, ax2]):
            ax.set_xlabel(xlabels[i])
            ax.set_ylabel(ylabels[i])
            ax.minorticks_on()
            ax.grid("major")
            ax.grid("minor", linestyle=":")
            ax.legend()

        fig.suptitle(self.airfoil_name)
        fig.tight_layout()
        plt.show(block=True)
