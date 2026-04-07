import React from 'react'
import { Outlet } from 'react-router-dom'
import { Layout as AntLayout } from 'antd'
import Header from './Header'
import SideMenu from './SideMenu'
import Footer from './Footer'
import './Layout.css'

const { Content } = AntLayout

const Layout: React.FC = () => {
  return (
    <AntLayout className="app-layout">
      <Header />
      <AntLayout>
        <SideMenu />
        <AntLayout className="main-content">
          <Content className="content-wrapper">
            <Outlet />
          </Content>
          <Footer />
        </AntLayout>
      </AntLayout>
    </AntLayout>
  )
}

export default Layout