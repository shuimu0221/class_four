#include "pose_solver.hpp"

#include <limits>

namespace auto_aim
{
PoseSolver::PoseSolver(
  const cv::Matx33d & camera_matrix, const cv::Vec<double, 5> & distort_coeffs)
: camera_matrix_(camera_matrix), distort_coeffs_(distort_coeffs)
{
}

// Task 01：在装甲板局部坐标系中填写四个灯条端点的 3D 坐标。
// 点序必须固定为：左上、右上、右下、左下。
std::vector<cv::Point3f> PoseSolver::object_points() const
{
  return {};
}

// Task 03：调用 cv::solvePnP，求出装甲板相对相机的 rvec 与 tvec。
std::optional<PoseResult> PoseSolver::solve(const std::vector<cv::Point2f> & image_points) const
{
  if (image_points.size() != 4) return std::nullopt;

  const auto points_3d = object_points();
  if (points_3d.size() != image_points.size()) return std::nullopt;

  return std::nullopt;
}

// Task 04：把 PnP 的 3D 点重新投影回图像，用于检查点序和标定参数。
std::vector<cv::Point2f> PoseSolver::reproject(const PoseResult & pose) const
{
  return {};
}

// Task 04：计算观测点与重投影点之间的 RMS 误差，单位为像素。
double PoseSolver::reprojection_rms(
  const std::vector<cv::Point2f> & image_points,
  const std::vector<cv::Point2f> & reprojected_points) const
{
  return std::numeric_limits<double>::infinity();
}

// Task 05：用 tvec 的模长表示目标距相机的直线距离，单位为米。
double PoseSolver::distance_m(const PoseResult & pose)
{
  return 0.0;
}

// Task 05：相机坐标系约定为 x 向右、y 向下、z 向前。
// 返回 {水平瞄准角 yaw, 俯仰瞄准角 pitch}，单位为度。
cv::Vec2d PoseSolver::aim_angles_deg(const cv::Vec3d & tvec)
{
  return {0.0, 0.0};
}
}  // namespace auto_aim
