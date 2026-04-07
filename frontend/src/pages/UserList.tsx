import React from 'react'
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import { Row, Col, Card } from 'antd'
import type { CellProps } from 'recharts'

const UserList: React.FC = () => {
  // 颜色配置
  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8', '#82ca9d']
  
  // 部门分布数据
  const departmentData = [
    { name: '管理层', value: 20 },
    { name: '分析部', value: 35 },
    { name: '技术部', value: 30 },
    { name: '市场部', value: 15 },
    { name: '教育部', value: 10 },
    { name: '其他', value: 10 }
  ]
  
  // 角色分布数据
  const roleData = [
    { name: '管理员', value: 5 },
    { name: '编辑', value: 20 },
    { name: '查看者', value: 35 },
    { name: '普通用户', value: 50 }
  ]
  
  return (
    <div style={{ padding: '20px' }}>
      <h2>用户列表</h2>
      
      <Row gutter={[16, 16]}>
        <Col span={24}>
          <Card title="用户角色分布" style={{ marginBottom: '20px' }}>
            <ResponsiveContainer width="100%" height={250}>
              <PieChart>
                <Pie
                  data={roleData}
                  cx="50%"
                  cy="50%"
                  labelLine={true}
                  label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                  outerRadius={80}
                  dataKey="value"
                >
                  {roleData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </Card>
        </Col>
        
        <Col span={24}>
          <Card title="用户部门分布" style={{ marginBottom: '20px' }}>
            <div style={{ width: '100%', height: 300 }}>
              <ResponsiveContainer width="100%" height="100%">
                <BarChart
                  data={departmentData}
                  margin={{ top: 20, right: 30, left: 20, bottom: 20 }}
                  layout="vertical"
                >
                  <CartesianGrid strokeDasharray="3 3" horizontal={false} />
                  <XAxis type="number" domain={[0, 'dataMax + 5']} />
                  <YAxis dataKey="name" type="category" width={80} />
                  <Tooltip 
                    contentStyle={{ backgroundColor: 'white', border: '1px solid #ccc' }}
                    formatter={(value) => [`${value}人`, '用户数量']}
                  />
                  <Legend verticalAlign="top" height={36} />
                  <Bar 
                    dataKey="value" 
                    name="用户数量" 
                    animationDuration={1500}
                    radius={[0, 4, 4, 0]}
                  >
                    {departmentData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </Card>
        </Col>
      </Row>
    </div>
  )
}

export default UserList