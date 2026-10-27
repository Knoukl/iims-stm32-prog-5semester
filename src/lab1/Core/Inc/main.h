/* USER CODE BEGIN Header */
/**
 ******************************************************************************
 * @file           : main.h
 * @brief          : Header for main.c file.
 *                   This file contains the common defines of the application.
 ******************************************************************************
 */
/* USER CODE END Header */

/* Define to prevent recursive inclusion -------------------------------------*/
#ifndef __MAIN_H
#define __MAIN_H

#ifdef __cplusplus
extern "C"
{
#endif

/* Includes ------------------------------------------------------------------*/
#include "stm32f1xx_hal.h"

  /* Exported functions prototypes ---------------------------------------------*/
  void Error_Handler(void);

/* Private defines -----------------------------------------------------------*/
#define TRAF_RED_Pin GPIO_PIN_2
#define TRAF_RED_GPIO_Port GPIOD
#define TRAF_YELLOW_Pin GPIO_PIN_1
#define TRAF_YELLOW_GPIO_Port GPIOD
#define TRAF_GREEN_Pin GPIO_PIN_0
#define TRAF_GREEN_GPIO_Port GPIOD
#define PED_RED_Pin GPIO_PIN_5
#define PED_RED_GPIO_Port GPIOD
#define PED_GREEN_Pin GPIO_PIN_4
#define PED_GREEN_GPIO_Port GPIOD
#define BUT_Pin GPIO_PIN_7
#define BUT_GPIO_Port GPIOD

#ifdef __cplusplus
}
#endif

#endif /* __MAIN_H */
