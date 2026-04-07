const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

console.log('正在设置Node.js环境...');

// 检查npm是否需要安装
if (!fs.existsSync(path.join(__dirname, 'node_modules'))) {
  console.log('正在创建package-lock.json文件...');
  fs.writeFileSync(path.join(__dirname, 'package-lock.json'), '{"lockfileVersion": 3}');
  
  console.log('正在创建简单的npm包装脚本...');
  const npmWrapper = `const { spawn } = require('child_process');
const path = require('path');
const args = process.argv.slice(2);

// 使用npm的在线安装方式
const cmd = process.platform === 'win32' ? 'cmd.exe' : 'bash';
const cmdArgs = process.platform === 'win32' 
  ? ['/c', 'powershell', '-Command', `Invoke-WebRequest -Uri https://registry.npmjs.org/npm/-/npm-10.5.0.tgz -OutFile npm.tgz; tar -xf npm.tgz; cd package; node ./bin/npm-cli.js ${args.join(' ')}`]
  : ['-c', `curl -L https://registry.npmjs.org/npm/-/npm-10.5.0.tgz -o npm.tgz; tar -xf npm.tgz; cd package; node ./bin/npm-cli.js ${args.join(' ')}`];

const child = spawn(cmd, cmdArgs, {
  stdio: 'inherit',
  cwd: process.cwd()
});

child.on('close', (code) => {
  process.exit(code);
});`;

  fs.writeFileSync(path.join(__dirname, 'npm-wrapper.js'), npmWrapper);
  
  console.log('npm包装脚本已创建，现在尝试安装项目依赖...');
  
  try {
    // 运行npm-wrapper.js来安装依赖
    execSync(`..\\node.exe npm-wrapper.js install`, { stdio: 'inherit', cwd: __dirname });
    
    console.log('\n依赖安装成功！现在尝试构建项目...');
    execSync(`..\\node.exe npm-wrapper.js run build`, { stdio: 'inherit', cwd: __dirname });
    
    console.log('\n🎉 环境设置完成！项目已成功构建。');
    console.log('\n您可以使用以下命令启动开发服务器：');
    console.log('..\\node.exe npm-wrapper.js run dev');
  } catch (error) {
    console.error('\n❌ 环境设置过程中出现错误：', error.message);
    console.log('\n请尝试手动安装Node.js，然后在frontend目录运行 npm install 和 npm run build');
  }
} else {
  console.log('node_modules文件夹已存在，跳过安装过程。');
  console.log('\n您可以使用以下命令启动开发服务器：');
  console.log('..\\node.exe npm-wrapper.js run dev');
}