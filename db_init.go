package main

import (
	"fmt"
	"io/ioutil"
	"log"
	"os"

	"gorm.io/driver/postgres"
	"gorm.io/gorm"
	"gorm.io/gorm/logger"

	"nftagent/models"
)

// initDB 初始化数据库
func initDB() (*gorm.DB, error) {
	// 获取数据库连接信息
	host := os.Getenv("DB_HOST")
	if host == "" {
		host = "localhost"
	}

	port := os.Getenv("DB_PORT")
	if port == "" {
		port = "5432"
	}

	user := os.Getenv("DB_USER")
	if user == "" {
		user = "postgres"
	}

	password := os.Getenv("DB_PASSWORD")
	if password == "" {
		password = "112358"
	}

	dbname := os.Getenv("DB_NAME")
	if dbname == "" {
		dbname = "postgres"
	}

	dsn := fmt.Sprintf("host=%s user=%s password=%s dbname=%s port=%s sslmode=disable",
		host, user, password, dbname, port)

	// 连接数据库
	db, err := gorm.Open(postgres.Open(dsn), &gorm.Config{
		Logger: logger.Default.LogMode(logger.Info),
	})
	if err != nil {
		return nil, fmt.Errorf("数据库连接失败: %v", err)
	}

	// 执行SQL脚本进行初始化
	sql, err := ioutil.ReadFile("db_init.sql")
	if err != nil {
		log.Printf("警告: 无法读取db_init.sql文件: %v", err)
	} else {
		if err := db.Exec(string(sql)).Error; err != nil {
			log.Printf("警告: SQL脚本执行失败: %v", err)
		}
	}

	// 自动迁移表结构
	err = db.AutoMigrate(
		&models.Agent{},
		&models.Conversation{},
		&models.Message{},
	)
	if err != nil {
		return nil, fmt.Errorf("表结构迁移失败: %v", err)
	}

	return db, nil
}
