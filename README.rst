
Proyecto Envelope-Sur
*********************


Interfaz de cálculo
--------------------

La biblioteca de cálculo del software de cálculo de envolventes y flashes se programará
en Fortran, de manera modular para facilitar la integración a un entorno de alto nivel
en Python a través de F2py_

Los cálculos de envolventes serán 3 rutinas de cálculo, 1 para cada modelo
(SRK, RKPR y PR). Estas rutinas reciben basicamente el mismo input, con la excepción
de los parámetros del modelo.

La interfaz básica

.. code-block:: python

    env_rkpr(n, comp, tc, pc, ohm, ac, b, del, k, Kij0, Kij1, Lij, To, Po, Do, Tcri, Pcri)


        system input parameters

            :param integer n: number of compound in the mixture (lenght of the system)
            :param array(n:float) comp: fraction of each compound (sum is 1.0)
            :param array(n:float) tc: Critical temperature of each compound
            :param array(n:float) pc: Critical pressure of each compound
            :param array(n:float) ohm: Acentric factor of each compound

        eos parameter (RKPR)

            :param array(n:float) ac: Critical value of the attractive parameter
                                      for each compound
            :param array(n:float) b: Repulsive parameter for each compound
            :param array(n:float) del: RK-PR third parameter for each compound
            :param array(n:float) k: Parameter for the temperature dependence of
                                     the attractive parameter for each compound

        Mixture rule input parameters

            This parameteres are a square adjacency matrixs (n x n) with a coefficient
            for binary relations. For example, suppose n= 2, Kij0 would be:

                                            c1    c2          c3
                                        c1 [0  Kij0_c1_c2 Kij0_c1_c3]
                                        c2 [       0      Kij0_c2_c3]
                                        c3 [                 0      ]

            where Kij0_c1_c2 is the Kij0 coefficient for the compound c1 and the compound c2

            In addition, Kij is temperature dependent, where each Kij is

                    Kij = Kij0 * exp(-T / Kij1)


            :param array(n x n:float) Kij0: Square adjacency matrix of Kij0
                                            between each compound.


            :param array(n x n:float) Kij1: Square adjacency matrix of Kij1
                                            between each compound.

            :param array(n x n:float) Lij: Square adjacency matrix of Lij
                                           between each compound.





.. _F2py: http://www.f2py.com





