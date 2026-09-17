#ifndef AUTO_AIM__POSE_SOLVER_HPP
#define AUTO_AIM__POSE_SOLVER_HPP

#include <opencv2/calib3d.hpp>
#include <opencv2/core.hpp>

#include <optional>
#include <vector>

namespace auto_aim
{
inline constexpr double kLightbarLengthM = 0.056;
inline constexpr double kSmallArmorLightbarDistanceM = 0.135;

struct PoseResult
{
  cv::Vec3d rvec;
  cv::Vec3d tvec;
};

class PoseSolver
{
public:
  PoseSolver(const cv::Matx33d & camera_matrix, const cv::Vec<double, 5> & distort_coeffs);

  std::vector<cv::Point3f> object_points() const;
  std::optional<PoseResult> solve(const std::vector<cv::Point2f> & image_points) const;
  std::vector<cv::Point2f> reproject(const PoseResult & pose) const;
  double reprojection_rms(
    const std::vector<cv::Point2f> & image_points,
    const std::vector<cv::Point2f> & reprojected_points) const;

  static double distance_m(const PoseResult & pose);
  static cv::Vec2d aim_angles_deg(const cv::Vec3d & tvec);

private:
  cv::Matx33d camera_matrix_;
  cv::Vec<double, 5> distort_coeffs_;
};
}  // namespace auto_aim

#endif  // AUTO_AIM__POSE_SOLVER_HPP
