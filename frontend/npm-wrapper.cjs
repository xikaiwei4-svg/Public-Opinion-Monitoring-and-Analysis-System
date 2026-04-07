const { spawn } = require('child_process');
const path = require('path');
const args = process.argv.slice(2);

// 创建一个简单的命令来下载和使用npm
const cmd = 'powershell';
const cmdArgs = ['-Command', 'Set-ExecutionPolicy Bypass -Scope Process -Force; ' +
  'Invoke-WebRequest -Uri "https://registry.npmjs.org/npm/-/npm-10.5.0.tgz" -OutFile npm.tgz; ' +
  'tar -xf npm.tgz; ' +
  'cd package; ' +
  'node ./bin/npm-cli.js ' + args.join(' ')];

const child = spawn(cmd, cmdArgs, {
  stdio: 'inherit',
  cwd: process.cwd()
});

child.on('close', (code) => {
  process.exit(code);
});