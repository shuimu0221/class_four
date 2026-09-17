#include "tasks/detector.hpp"
#include "tasks/pose_solver.hpp"
#include "tools/img_tools.hpp"

#include <fmt/format.h>

#include <iostream>
#include <string>
#include <vector>

namespace
{
const cv::Matx33d kCameraMatrix{
  1286.307063384126, 0.0, 645.34450819155256,
  0.0, 1288.1400736562441, 483.6163720308021,
  0.0, 0.0, 1.0,
};

const cv::Vec<double, 5> kDistortCoeffs{
  -0.47562935060124745,
  0.21831745829617311,
  0.0004957613589406044,
  -0.00034617769548693592,
  0.0,
};

constexpr int kCalibrationImageWidth = 1280;
constexpr int kCalibrationImageHeight = 1024;

void draw_marker(
  cv::Mat & image, const cv::Point2f & point, const cv::Scalar & color, const std::string & label)
{
  cv::circle(image, point, 5, color, 2, cv::LINE_AA);
  tools::draw_text(image, label, point + cv::Point2f(6.0F, -6.0F), 0.45, color, 1);
}

void draw_pose_overlay(
  cv::Mat & image,
  const auto_aim::PoseSolver & solver,
  const std::vector<cv::Point2f> & image_points,
  const auto_aim::PoseResult & pose)
{
  const auto reprojected_points = solver.reproject(pose);
  const double rms = solver.reprojection_rms(image_points, reprojected_points);
  const double range_m = auto_aim::PoseSolver::distance_m(pose);
  const cv::Vec2d aim_angles = auto_aim::PoseSolver::aim_angles_deg(pose.tvec);

  for (std::size_t i = 0; i < image_points.size(); ++i) {
    draw_marker(image, image_points[i], cv::Scalar(0, 0, 255), fmt::format("O{}", i + 1));
  }
  for (std::size_t i = 0; i < reprojected_points.size(); ++i) {
    draw_marker(image, reprojected_points[i], cv::Scalar(0, 255, 0), fmt::format("P{}", i + 1));
  }

  tools::draw_text(
    image,
    fmt::format("tvec [m]: x {:.2f}  y {:.2f}  z {:.2f}", pose.tvec[0], pose.tvec[1], pose.tvec[2]),
    cv::Point(10, 35), 0.65, cv::Scalar(0, 255, 255), 2);
  tools::draw_text(
    image,
    fmt::format("rvec [rad]: x {:.2f}  y {:.2f}  z {:.2f}", pose.rvec[0], pose.rvec[1], pose.rvec[2]),
    cv::Point(10, 65), 0.65, cv::Scalar(0, 255, 255), 2);
  tools::draw_text(
    image,
    fmt::format("range: {:.2f} m   aim yaw: {:.1f} deg   pitch: {:.1f} deg", range_m, aim_angles[0], aim_angles[1]),
    cv::Point(10, 95), 0.65, cv::Scalar(0, 255, 255), 2);
  tools::draw_text(
    image,
    fmt::format("reprojection RMS: {:.2f} px   red=observed, green=projected", rms),
    cv::Point(10, 125), 0.65, cv::Scalar(0, 255, 255), 2);
}
}  // namespace

int main()
{
  try {
    auto_aim::Detector detector;
    const auto_aim::PoseSolver pose_solver(kCameraMatrix, kDistortCoeffs);

    cv::VideoCapture cap("video.avi");
    if (!cap.isOpened()) {
      std::cerr << "Cannot open video. Build the target first, then run it from the build directory." << std::endl;
      return 1;
    }

    cv::Mat image;
    while (cap.read(image)) {
      if (image.cols != kCalibrationImageWidth || image.rows != kCalibrationImageHeight) {
        tools::draw_text(
          image, "Warning: image size differs from the calibration used in this lesson.",
          cv::Point(10, 30), 0.55, cv::Scalar(0, 0, 255), 2);
      }

      const auto armors = detector.detect(image);
      if (!armors.empty()) {
        const auto & armor = armors.front();
        tools::draw_points(image, armor.points, cv::Scalar(0, 0, 255), 1);

        // Task 02：把 2D 像素点按左上、右上、右下、左下的顺序填入。
        // 现在保留为空，使工程在开始做题前也可以编译运行。
        const std::vector<cv::Point2f> image_points{};

        const auto pose = pose_solver.solve(image_points);
        if (pose.has_value()) {
          draw_pose_overlay(image, pose_solver, image_points, *pose);
        } else {
          tools::draw_text(
            image, "Pose not solved yet. Complete Task 01 to Task 03.",
            cv::Point(10, 35), 0.65, cv::Scalar(0, 255, 255), 2);
        }
      } else {
        tools::draw_text(image, "No armor detected", cv::Point(10, 35), 0.65, cv::Scalar(0, 255, 255), 2);
      }

      cv::imshow("Lecture 4 pose estimation. Press q to quit.", image);
      if (cv::waitKey(20) == 'q') break;
    }
  } catch (const cv::Exception & error) {
    std::cerr << "OpenCV error: " << error.what() << std::endl;
    return 1;
  }

  cv::destroyAllWindows();
  return 0;
}
