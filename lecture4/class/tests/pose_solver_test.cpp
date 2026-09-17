#include "tasks/pose_solver.hpp"

#include <cmath>
#include <cstdlib>
#include <iostream>
#include <string>
#include <vector>

namespace
{
void require(bool condition, const std::string & message)
{
  if (!condition) {
    std::cerr << "FAIL: " << message << std::endl;
    std::exit(EXIT_FAILURE);
  }
}
}  // namespace

int main()
{
  const cv::Matx33d camera_matrix{
    1280.0, 0.0, 640.0,
    0.0, 1280.0, 512.0,
    0.0, 0.0, 1.0,
  };
  const cv::Vec<double, 5> distort_coeffs{0.0, 0.0, 0.0, 0.0, 0.0};
  const auto_aim::PoseSolver solver(camera_matrix, distort_coeffs);

  // 固定的物理尺寸和点序。测试不能从学生实现反推期望值，
  // 否则错误的装甲板尺寸也可能通过“自洽”的 PnP 检查。
  const std::vector<cv::Point3f> expected_object_points{
    {-0.0675F, -0.028F, 0.0F},
    {0.0675F, -0.028F, 0.0F},
    {0.0675F, 0.028F, 0.0F},
    {-0.0675F, 0.028F, 0.0F},
  };
  const auto object_points = solver.object_points();
  require(object_points.size() == expected_object_points.size(), "应返回四个装甲板 3D 点");
  for (std::size_t i = 0; i < expected_object_points.size(); ++i) {
    const cv::Point3f error = object_points[i] - expected_object_points[i];
    require(
      std::abs(error.x) < 1e-6F && std::abs(error.y) < 1e-6F && std::abs(error.z) < 1e-6F,
      "3D 点的尺寸或左上、右上、右下、左下顺序不符合约定");
  }

  const cv::Vec3d expected_rvec{0.10, -0.15, 0.08};
  const cv::Vec3d expected_tvec{0.12, -0.08, 2.00};
  std::vector<cv::Point2f> image_points;
  cv::projectPoints(
    expected_object_points, expected_rvec, expected_tvec, camera_matrix, distort_coeffs, image_points);

  const auto pose = solver.solve(image_points);
  require(pose.has_value(), "四个有效对应点应当能够解出位姿");
  require(cv::norm(pose->tvec - expected_tvec) < 1e-3, "tvec 应当恢复已知平移");

  const auto reprojected_points = solver.reproject(*pose);
  require(reprojected_points.size() == image_points.size(), "重投影点数量应与输入点一致");
  require(
    solver.reprojection_rms(image_points, reprojected_points) < 1e-3,
    "无畸变的合成点应具有接近零的重投影误差");

  const auto [yaw_deg, pitch_deg] = auto_aim::PoseSolver::aim_angles_deg(pose->tvec);
  const double expected_yaw_deg = std::atan2(expected_tvec[0], expected_tvec[2]) * 180.0 / CV_PI;
  const double expected_pitch_deg =
    std::atan2(-expected_tvec[1], std::hypot(expected_tvec[0], expected_tvec[2])) * 180.0 / CV_PI;
  require(std::abs(yaw_deg - expected_yaw_deg) < 1e-3, "水平瞄准角应由 tvec 的 x 和 z 计算");
  require(std::abs(pitch_deg - expected_pitch_deg) < 1e-3, "俯仰瞄准角应考虑相机 y 轴向下");

  const std::vector<cv::Point2f> incomplete_points(image_points.begin(), image_points.begin() + 3);
  require(!solver.solve(incomplete_points).has_value(), "少于四个点时应拒绝求解");

  std::cout << "PASS: PoseSolver synthetic PnP checks" << std::endl;
  return EXIT_SUCCESS;
}
