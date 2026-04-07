import { exec } from 'node:child_process';

console.log('Starting Vite development server...');
exec('npx vite@latest dev', { cwd: 'd:\\360zip\\project1\\frontend' }, (error, stdout, stderr) => {
  if (error) {
    console.error(`Error: ${error.message}`);
    return;
  }
  if (stderr) {
    console.error(`stderr: ${stderr}`);
    return;
  }
  console.log(`stdout: ${stdout}`);
});