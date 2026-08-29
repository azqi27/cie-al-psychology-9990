import { defineConfig } from 'astro/config';
import tailwindcss from '@tailwindcss/vite';

// 部署到 GitHub Pages 项目站点：
//   站点地址 = https://azqi27.github.io/cie-al-psychology-9990/
// base 必须与该仓库名一致；site 用于生成绝对链接。
export default defineConfig({
  site: 'https://azqi27.github.io',
  base: '/cie-al-psychology-9990',
  vite: {
    plugins: [tailwindcss()],
  },
});
