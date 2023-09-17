import numpy as np

def perspective_ray(resolution, intrinsic, extrinsic):
  '''
  Construct input ray for perspective camera model
  # Arguments
  * `resolution`: tuple of 2 integers [`width`, `height`]
  * `intrinsic`: 3 * 3 matrix
  * `extrinsic`: 4 * 4 matrix
  # Return
  * 18 * `height` * `width`
  Camera model use x-right, y-down, z-forward axis scheme
  '''
  intrinsic_inv = np.linalg.inv(intrinsic)
  extrinsic_inv = np.linalg.inv(extrinsic)
  axis_x = np.linspace(
	  0.5 - 0.5 * resolution[0] / max(*resolution),
    0.5 + 0.5 * resolution[0] / max(*resolution),
    resolution[0] + 1, dtype=np.float32)[:, np.newaxis]
  axis_y = np.linspace(
    0.5 - 0.5 * resolution[1] / max(*resolution),
    0.5 + 0.5 * resolution[1] / max(*resolution),
    resolution[1] + 1, dtype=np.float32)[np.newaxis,:]
  axis_z = np.array([[1.0]], dtype=np.float32)
  axis_xyz = np.stack(np.broadcast_arrays(axis_x, axis_y, axis_z), axis=-1)
  axis_xyz = np.matmul(intrinsic_inv, axis_xyz[..., np.newaxis])

  axis_xyz /= np.linalg.norm(axis_xyz, ord=2, axis=2, keepdims=True)
  ret_rd = np.matmul(extrinsic_inv[:3,:3], axis_xyz).squeeze(-1)
  ret_rd = np.concatenate([ret_rd[:-1,:-1, ...],
    ret_rd[:-1, 1:, ...] - ret_rd[:-1,:-1, ...],
    ret_rd[1:,:-1, ...] - ret_rd[:-1,:-1, ...]], axis=-1)
  ret_rd = ret_rd.transpose(2, 1, 0)
  ret_r = np.array([0.0, 0.0, 0.0, 1.0], dtype=np.float32)[:, np.newaxis]
  ret_r = np.matmul(extrinsic_inv, ret_r)[:3, :, np.newaxis]
  ret_r = np.broadcast_to(ret_r, (3, resolution[1], resolution[0]))
  ret_r = np.concatenate([ret_r] + [np.zeros_like(ret_r)] * 2, axis=0)
  return np.concatenate([ret_r, ret_rd], axis=0)
