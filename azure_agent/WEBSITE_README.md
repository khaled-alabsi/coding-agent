# Personal Website

A modern, responsive personal portfolio website built with React and TypeScript.

## Features

- ✅ Responsive design for all devices
- ✅ Modern UI with smooth animations
- ✅ Sections: Home, About, Projects, Blog, Contact
- ✅ Built with React + TypeScript + Vite

## Quick Start

### 1. Install Dependencies

```bash
npm install
```

### 2. Start Development Server

```bash
npm run dev
```

The website will open at `http://localhost:5173`

### 3. Build for Production

```bash
npm run build
```

The optimized files will be in the `dist/` folder.

### 4. Preview Production Build

```bash
npm run preview
```

## Project Structure

```
azure_agent/
├── src/
│   ├── components/      # React components
│   │   ├── Header.tsx   # Navigation header
│   │   ├── Hero.tsx     # Hero section
│   │   ├── About.tsx    # About me section
│   │   ├── Projects.tsx # Projects showcase
│   │   ├── Blog.tsx     # Blog posts
│   │   ├── Contact.tsx  # Contact form
│   │   └── Footer.tsx   # Footer
│   ├── styles/          # CSS files
│   │   └── main.css     # Main stylesheet
│   ├── data/            # JSON data
│   ├── App.tsx          # Main app component
│   ├── index.tsx        # Entry point
│   └── index.html       # HTML template
├── package.json
├── tsconfig.json
└── vite.config.ts
```

## Customization

### Change Personal Info

1. Edit `src/components/Hero.tsx` - Update your name and title
2. Edit `src/components/About.tsx` - Update your bio and skills
3. Edit `src/components/Projects.tsx` - Add your projects
4. Edit `src/components/Blog.tsx` - Add your blog posts
5. Edit `src/components/Contact.tsx` - Update contact information

### Styling

All styles are in `src/styles/main.css`. Customize colors, fonts, and layout as needed.

## Technologies Used

- **React** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool and dev server
- **CSS3** - Styling
- **Font Awesome** - Icons

## Deployment

You can deploy this website to:

- **Vercel**: `vercel deploy`
- **Netlify**: Drag and drop the `dist` folder
- **GitHub Pages**: Use the `dist` folder

## Need Help?

Check out:
- [React Documentation](https://react.dev/)
- [Vite Documentation](https://vitejs.dev/)
- [TypeScript Documentation](https://www.typescriptlang.org/)

---

Built with ❤️ using React + TypeScript
