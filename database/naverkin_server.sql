/*
SQLyog Community v13.2.0 (64 bit)
MySQL - 10.4.28-MariaDB : Database - naverkin_server
*********************************************************************
*/

/*!40101 SET NAMES utf8 */;

/*!40101 SET SQL_MODE=''*/;

/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;
/*Table structure for table `account_interactions` */

DROP TABLE IF EXISTS `account_interactions`;

CREATE TABLE `account_interactions` (
  `username` varchar(30) NOT NULL,
  `interacted_accounts` text DEFAULT NULL,
  PRIMARY KEY (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

/*Table structure for table `crawler_configs` */

DROP TABLE IF EXISTS `crawler_configs`;

CREATE TABLE `crawler_configs` (
  `config_id` int(11) NOT NULL,
  `submit_delay` int(11) DEFAULT NULL,
  `page_refresh` int(11) DEFAULT NULL,
  `cooldown` int(11) DEFAULT NULL,
  `prohibited_words` text DEFAULT NULL,
  `prescript` text DEFAULT NULL,
  `prompt` text DEFAULT NULL,
  `postscript` text DEFAULT NULL,
  `max_interactions` int(11) DEFAULT NULL,
  `openai_api_key` varchar(64) DEFAULT NULL,
  PRIMARY KEY (`config_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

/*Table structure for table `naverkin_question` */

DROP TABLE IF EXISTS `naverkin_question`;

CREATE TABLE `naverkin_question` (
  `question_id` varchar(255) NOT NULL,
  `question_title` varchar(255) DEFAULT NULL,
  `question_status` int(11) DEFAULT NULL,
  `author` varchar(30) DEFAULT NULL,
  `respondent_user` varchar(30) DEFAULT NULL,
  PRIMARY KEY (`question_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

/*Table structure for table `naverkin_user` */

DROP TABLE IF EXISTS `naverkin_user`;

CREATE TABLE `naverkin_user` (
  `username` varchar(30) NOT NULL,
  `passwd` varchar(30) DEFAULT NULL,
  `recovery_email` varchar(100) DEFAULT NULL,
  `account_name` varchar(50) DEFAULT NULL,
  `date_of_birth` date DEFAULT NULL,
  `gender` varchar(20) DEFAULT NULL,
  `mobile_no` varchar(30) DEFAULT NULL,
  `levelup_id` int(11) DEFAULT NULL,
  `account_url` varchar(255) DEFAULT NULL,
  `account_status` int(11) DEFAULT NULL,
  PRIMARY KEY (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

/*Table structure for table `user_session` */

DROP TABLE IF EXISTS `user_session`;

CREATE TABLE `user_session` (
  `username` varchar(30) NOT NULL,
  `cookies` text DEFAULT NULL,
  `user_agent` text DEFAULT NULL,
  PRIMARY KEY (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;
