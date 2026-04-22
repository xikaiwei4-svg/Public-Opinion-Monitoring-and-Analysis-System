import React from 'react'
import { Layout, Typography, Row, Col } from 'antd'

const { Footer: AntFooter } = Layout
const { Text } = Typography

const Footer: React.FC = () => {
  // 获取当前年份
  const currentYear = new Date().getFullYear()
  
  // 系统版本号（可以从配置文件或环境变量中读取）
  const systemVersion = 'v1.0.0'
  
  return (
    <AntFooter className="bg-white border-t border-gray-200 py-4">
      <div className="container mx-auto px-4">
        <Row justify="space-between" align="middle">
          <Col>
            <Text type="secondary" className="block md:inline">
              © {currentYear} 校园舆情检测与热点话题分析系统. All rights reserved.
            </Text>
          </Col>
          <Col>
            <Text type="secondary" className="block md:inline">
              版本: {systemVersion}
            </Text>
          </Col>
          <Col>
            <Text type="secondary" className="block md:inline">
              技术支持: <a href="mailto:support@example.com" className="text-blue-600 hover:text-blue-800">support@example.com</a>
            </Text>
          </Col>
        </Row>

      </div>
    </AntFooter>
  )
}

export default Footer