# Copyright 2025 The Physics-Next Project Developers
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================

"""Tests for constraint functions."""

from absl.testing import absltest
from absl.testing import parameterized
from . import test_util
import mujoco
from mujoco import mjx
import numpy as np

# tolerance for difference between MuJoCo and MJX constraint calculations,
# mostly due to float precision
_TOLERANCE = 5e-5


def _assert_eq(a, b, name):
  tol = _TOLERANCE * 10  # avoid test noise
  err_msg = f"mismatch: {name}"
  np.testing.assert_allclose(a, b, err_msg=err_msg, atol=tol, rtol=tol)


class ConstraintTest(parameterized.TestCase):
  @parameterized.parameters(
    {
      "cone": mujoco.mjtCone.mjCONE_PYRAMIDAL,
    },
  )
  def test_constraints(self, cone):
    """Test constraints."""
    mjm, mjd, mx, dx = test_util.fixture("constraints.xml", sparse=False)
    mjm.opt.cone = cone

    for key in range(3):
      mujoco.mj_resetDataKeyframe(mjm, mjd, key)

      mujoco.mj_forward(mjm, mjd)
      mx = mjx.put_model(mjm)
      dx = mjx.put_data(mjm, mjd)
      dx = mjx.make_constraint(mx, dx)

      _assert_eq(mjd.efc_J, np.reshape(dx.efc_J.numpy(), shape=(mjd.nefc * mjm.nv)), "efc_J")
      _assert_eq(mjd.efc_D, np.reshape(dx.efc_D.numpy(), shape=(mjd.nefc)), "efc_D")
      _assert_eq(
        mjd.efc_aref, np.reshape(dx.efc_aref.numpy(), shape=(mjd.nefc)), "efc_aref"
      )
      _assert_eq(mjd.efc_pos, np.reshape(dx.efc_pos.numpy(), shape=(mjd.nefc)), "efc_pos")
      _assert_eq(
        mjd.efc_margin, np.reshape(dx.efc_margin.numpy(), shape=(mjd.nefc)), "efc_margin"
      )
      _assert_eq(
        mjd.efc_frictionloss,
        np.reshape(dx.efc_frictionloss.numpy(), shape=(mjd.nefc)),
        "efc_frictionloss",
      )


if __name__ == "__main__":
  absltest.main()
