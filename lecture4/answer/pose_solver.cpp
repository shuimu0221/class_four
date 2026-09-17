#include "tasks/pose_solver.hpp"

#include <cmath>
#include <limits>

namespace auto_aim
{
PoseSolver::PoseSolver(
  const cv::Matx33d & camera_matrix, const cv::Vec<double, 5> & distort_coeffs)
: camera_matrix_(camera_matrix), distort_coeffs_(distort_coeffs)
{
}

std::vector<cv::Point3f> PoseSolver::object_points() const
{
  const float half_width = static_cast<float>(kSmallArmorLightbarDistanceM / 2.0);
  const float half_height = static_cast<float>(kLightbarLengthM / 2.0);
  return {
    {-half_width, -half_height, 0.0F},
    {half_width, -half_height, 0.0F},
    {half_width, half_height, 0.0F},
    {-half_width, half_height, 0.0F},
  };
}

std::optional<PoseResult> PoseSolver::solve(const std::vector<cv::Point2f> & image_points) const
{
  const auto points_3d = object_points();
  if (image_points.size() != points_3d.size() || image_points.size() != 4) return std::nullopt;

  PoseResult pose;
  const bool solved = cv::solvePnP(
    points_3d, image_points, camera_matrix_, distort_coeffs_, pose.rvec, pose.tvec,
    false, cv::SOLVEPNP_ITERATIVE);
  if (!solved || pose.tvec[2] <= 0.0) return std::nullopt;

  return pose;
}

std::vector<cv::Point2f> PoseSolver::reproject(const PoseResult & pose) const
{
  std::vector<cv::Point2f> reprojected_points;
  cv::projectPoints(
    object_points(), pose.rvec, pose.tvec, camera_matrix_, distort_coeffs_, reprojected_points);
  return reprojected_points;
}

double PoseSolver::reprojection_rms(
  const std::vector<cv::Point2f> & image_points,
  const std::vector<cv::Point2f> & reprojected_points) const
{
  if (image_points.empty() || image_points.size() != reprojected_points.size()) {
    return std::numeric_limits<double>::infinity();
  }

  double squared_error_sum = 0.0;
  for (std::size_t i = 0; i < image_points.size(); ++i) {
    const cv::Point2f error = image_points[i] - reprojected_points[i];
    squared_error_sum += error.dot(error);
  }
  return std::sqrt(squared_error_sum / static_cast<double>(image_points.size()));
}

double PoseSolver::distance_m(const PoseResult & pose)
{
  return cv::norm(pose.tvec);
}

cv::Vec2d PoseSolver::aim_angles_deg(const cv::Vec3d & tvec)
{
  const double horizontal_distance = std::hypot(tvec[0], tvec[2]);
  const double yaw_deg = std::atan2(tvec[0], tvec[2]) * 180.0 / CV_PI;
  const double pitch_deg = std::atan2(-tvec[1], horizontal_distance) * 180.0 / CV_PI;
  return {yaw_deg, pitch_deg};
}
}  // namespace auto_aim
