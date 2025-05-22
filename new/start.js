#!/usr/bin/env node

// 简单的启动脚本，确保在正确的目录中运行Nuxt
const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

// 确保当前目录是项目根目录
const nuxtConfigPath = path.join(process.cwd(), 'nuxt.config.js');
if (!fs.existsSync(nuxtConfigPath)) {
  console.error('错误：请在项目根目录中运行此脚本');
  process.exit(1);
}

// 运行nuxt命令
const args = process.argv.slice(2);
const defaultCommand = 'dev';
const command = args.length > 0 ? args[0] : defaultCommand;

console.log(`正在运行: nuxt ${command}`);

const nuxt = spawn('npx', ['nuxt', command], {
  stdio: 'inherit',
  shell: true
});

nuxt.on('close', (code) => {
  process.exit(code);
});
