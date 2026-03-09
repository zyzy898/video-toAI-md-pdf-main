<template>
<div class="app-container">
        <header class="header">
            <span class="header-eyebrow">AI Workflow Studio</span>
            <div class="header-icon">
                <i data-lucide="video">
                <svg t="1773046679141" class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="5455" width="40" height="40"><path d="M861.44 246.8864a68.266667 68.266667 0 0 1 93.422933 58.965333l0.136534 4.3008 0.477866 232.5504a68.266667 68.266667 0 0 1-89.361066 65.0752l-4.061867-1.467733-157.832533-62.583467a34.133333 34.133333 0 0 1 22.647466-64.341333l2.5088 0.887467 157.832534 62.5664-0.477867-232.533334-157.2864 62.737067a34.133333 34.133333 0 0 1-27.733333-62.327467l2.440533-1.092266 157.2864-62.737067z" fill="#444444" p-id="5456"></path><path d="M682.666667 119.466667H136.533333a68.266667 68.266667 0 0 0-68.266666 68.266666v477.866667a68.266667 68.266667 0 0 0 68.266666 68.266667h546.133334a68.266667 68.266667 0 0 0 68.266666-68.266667V187.733333a68.266667 68.266667 0 0 0-68.266666-68.266666zM136.533333 187.733333h546.133334v477.866667H136.533333V187.733333z" fill="#444444" p-id="5457"></path><path d="M242.5344 701.5424a34.133333 34.133333 0 0 1 62.1568 28.091733l-1.092267 2.423467-85.333333 170.666667a34.133333 34.133333 0 0 1-62.1568-28.091734l1.092267-2.423466 85.333333-170.666667zM530.875733 686.267733a34.133333 34.133333 0 0 1 44.509867 12.919467l1.28 2.3552 85.333333 170.666667a34.133333 34.133333 0 0 1-59.784533 32.8704l-1.28-2.3552-85.333333-170.666667a34.133333 34.133333 0 0 1 15.274666-45.789867z" fill="#444444" p-id="5458"></path><path d="M512 529.066667v34.133333a34.133333 34.133333 0 0 1-34.133333 34.133333H238.933333a34.133333 34.133333 0 0 1-34.133333-34.133333v-34.133333h307.2z" fill="#00B386" p-id="5459"></path></svg>
            </i>
            </div>
            <h1>视频转文档</h1>
            <p>AI 自动分析视频，生成带截图的分步总结文档</p>
            <div class="header-chips">
                <span class="header-chip">Whisper</span>
                <span class="header-chip">Batch Ready</span>
                <span class="header-chip">Markdown + PDF</span>
            </div>
        </header>

        <div class="main-grid">
            <div class="sidebar">
                <div class="card">
                    <div class="card-header">
                        <i data-lucide="settings">
                            <svg t="1773047661729" class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="13251" width="200" height="200"><path d="M571.06 957.11H453.14c-37.5 0-72.68-26.47-83.4-62.14-2.76-5.92-6.63-15.3-9.57-26.78-7.21 5.58-14.28 10.74-22.3 14.76-18.62 9.3-30.34 9.3-43.92 9.3-20.62 0-40.2-9.14-58.21-27.14l-82.55-82.55c-26.3-26.31-30.76-64.5-11.93-102.13l2.33-4.68 3.7-3.7c2.86-2.87 5.91-7.82 9.14-13.17-0.9-0.17-1.8-0.33-2.66-0.48-4.79-0.88-10.75-1.98-13.12-1.98l-7.83-0.97c-37.48-9.37-65.74-45.65-65.74-84.38V453.15c0-38.75 28.27-75.03 65.75-84.4l7.82-0.96c2.37 0 8.33-1.09 13.12-1.98 0.58-0.11 1.18-0.21 1.78-0.33-5.4-7.01-10.4-13.92-14.3-21.72-18.82-37.64-14.36-75.82 11.93-102.13l86.01-80.29c13.76-20.15 40.22-29.4 60.64-29.4 7.58 0 25.31 0 43.93 9.3l4.69 2.34 3.7 3.71c3.91 3.91 8.11 7.14 12.88 10.72 0.26-1.46 0.52-2.88 0.77-4.26 0.88-4.78 1.98-10.74 1.98-13.11l0.96-7.82c9.37-37.48 45.65-65.75 84.4-65.75h117.92c37.49 0 72.67 26.46 83.4 62.13a155.84 155.84 0 0 1 9.57 26.79c7.2-5.57 14.28-10.74 22.3-14.76 18.62-9.3 30.34-9.3 43.92-9.3 20.6 0 40.19 9.14 58.21 27.15l82.53 82.53c26.31 26.3 30.77 64.48 11.95 102.14l-2.34 4.69-3.71 3.7c-2.92 2.93-6.06 8.04-9.36 13.55 5.91 1.18 10.73 2.07 16.01 2.07l7.82 0.96c37.48 9.36 65.74 45.65 65.74 84.4v117.92c0 38.74-28.26 75.02-65.72 84.38l-7.83 0.97c-2.37 0-8.33 1.09-13.12 1.98-0.58 0.11-1.18 0.21-1.78 0.33 4.99 6.49 9.65 12.88 13.4 19.98 17.73 28.37 18.51 74.29-11.06 103.85l-79.72 79.74c-13.66 20.53-40.42 29.95-61.03 29.95-15.6 0-36.95 0-52.31-15.36-3.08-3.07-8.58-6.37-14.4-9.87-0.59-0.35-1.19-0.7-1.78-1.06-0.02 0.11-0.05 0.22-0.07 0.34-1.51 7.57-3.22 16.11-6.57 26.38-9.87 36.85-45.76 64.46-84.05 64.46zM385.1 799.33c0.53 0.18 1.07 0.35 1.61 0.53 6.4 2.13 16.07 5.36 24.41 13.7l9.46 9.46v13.37c0 11.76 4.33 24.61 8.38 32.7l2.46 6.63c2.19 8.79 12.54 16.8 21.72 16.8h117.92c9.17 0 19.52-8.01 21.73-16.81l0.69-2.39c2.31-6.93 3.49-12.85 4.87-19.7 1.57-7.83 3.34-16.7 6.93-27.46l2.41-7.21 5.37-5.38c8.34-8.36 18.02-11.58 24.43-13.72 0.53-0.18 1.06-0.35 1.59-0.53l20.42-20.41 22.83 22.83c3.09 3.09 8.6 6.39 14.43 9.89 7.2 4.32 15.22 9.14 22.8 15.8 4.99 0.37 13.68 0.62 18.26-1.79l1.26-2.51 86.24-86.25c6.24-6.24 5.45-18.73 1.86-24.09l-2.02-3.48c-1.86-3.74-6.32-9.44-11.04-15.49-5.11-6.55-10.75-13.82-16.42-22.32l-14.69-22.02 16.31-16.31c0.17-0.53 0.34-1.06 0.52-1.59 2.13-6.4 5.36-16.07 13.7-24.41l9.46-9.46h13.37c6.79 0 14.73-1.45 22.39-2.86 6.58-1.21 12.89-2.37 19.22-2.83 7.85-3.24 14.53-12.6 14.53-20.97v-117.9c0-8.3-6.56-17.59-14.33-20.89-9.66-0.47-17.81-2.1-24.57-3.45-6.48-1.3-11.6-2.32-17.24-2.32H823l-9.46-9.46c-8.35-8.34-11.56-18.01-13.7-24.42-0.18-0.53-0.35-1.06-0.53-1.59L778.9 370.6l22.85-22.83c3.08-3.08 6.38-8.59 9.88-14.41 4.21-7.01 8.88-14.8 15.26-22.19 6.63-15.63 0.95-21.31-1.58-23.84l-82.53-82.53c-6.08-6.08-10.55-8.23-12.54-8.23-10.06 0-10.06 0-15.03 2.49-3.73 1.86-9.42 6.31-15.45 11.02-6.56 5.12-13.85 10.78-22.36 16.45l-22 14.65-16.3-16.28c-0.53-0.18-1.06-0.34-1.6-0.52-6.41-2.13-16.09-5.36-24.44-13.73l-9.44-9.45v-13.36c0-11.76-4.33-24.62-8.39-32.73l-2.44-6.61c-2.21-8.8-12.56-16.81-21.73-16.81H453.14c-8.38 0-17.73 6.68-20.97 14.53-0.46 6.34-1.62 12.64-2.83 19.22-1.41 7.67-2.86 15.6-2.86 22.4v19.96l-17.85 8.93c-7.97 3.97-14.09 6.01-19.01 7.65-3.14 1.05-6.31 2.05-10.5 4.14l-20.82 10.39-16.44-16.45c-4.27-4.27-8.88-7.73-14.22-11.73-4.96-3.72-10.43-7.83-16.15-12.99-4.14-1.19-8.52-1.19-11.65-1.19-2.22 0-5.69 1.03-7.56 2l-1.51 3.04-92.7 86.51c-1.91 1.94-8.28 8.32 0.97 26.81 1.86 3.74 6.32 9.44 11.03 15.47 5.12 6.56 10.76 13.82 16.42 22.32l14.68 22.01-17.48 17.5c-0.27 0.69-0.54 1.43-0.84 2.23-1.49 3.93-3.28 8.52-6.12 14.2l-8.93 17.85h-19.96c-6.79 0-14.73 1.45-22.39 2.86-6.59 1.21-12.89 2.37-19.23 2.83-7.85 3.24-14.53 12.59-14.53 20.97v117.92c0 8.37 6.68 17.72 14.54 20.97 6.33 0.46 12.64 1.62 19.22 2.83 7.66 1.41 15.6 2.86 22.39 2.86h13.37l9.46 9.46c8.35 8.34 11.57 18.02 13.71 24.42 0.17 0.54 0.34 1.07 0.52 1.6l20.37 20.41-22.8 22.81c-3.08 3.09-6.39 8.6-9.88 14.42-4.22 7.02-8.88 14.81-15.27 22.21-6.63 15.62-0.96 21.31 1.58 23.83l82.53 82.55c6.08 6.07 10.55 8.22 12.54 8.22 10.06 0 10.06 0 15.03-2.49 3.74-1.87 9.45-6.33 15.5-11.04 6.55-5.12 13.8-10.75 22.29-16.42l22.01-14.68 16.3 16.3z m338.47 31.87z m-6.37-4.06z m21.48-2.02zM291.42 199.09z" fill="#666666" p-id="13252"></path><path d="M512.09 668.22c-84.62 0-156.1-71.49-156.1-156.11 0-84.62 71.49-156.1 156.1-156.1 84.63 0 156.11 71.49 156.11 156.1 0.01 84.63-71.48 156.11-156.11 156.11z m0-247.62c-48.75 0-91.51 42.77-91.51 91.51 0 48.76 42.77 91.52 91.51 91.52 48.76 0 91.52-42.77 91.52-91.52 0.01-48.75-42.76-91.51-91.52-91.51z" fill="#666666" p-id="13253"></path></svg>
                        </i>
                        <h2>配置选项</h2>
                    </div>
                    <div class="card-body">
                        <div class="form-group">
                            <label class="form-label">
                                <span class="required">*</span> 火山引擎 ARK API Key
                            </label>
                            <input v-model.trim="apiKey" type="password" class="form-input" placeholder="ARK API Key" required>
                            <span class="form-hint">目前仅支持 doubao-seed-2-0-pro-260215</span>
                        </div>

                        <div class="form-group">
                            <label class="form-label">Whisper 字幕识别模型</label>
                            <select v-model="whisperModel" class="form-select">
                                <option value="tiny">tiny - 最快，精度较低</option>
                                <option value="base">base - 快速，平衡精度</option>
                                <option value="small">small - 中等速度，较高精度</option>
                                <option value="medium">medium - 较慢，更高精度</option>
                                <option value="large">large - 最慢，最高精度</option>
                            </select>
                        </div>

                        <div class="form-group">
                            <label class="form-label">AI 看图增强次数</label>
                            <input v-model.number="maxVision" type="number" class="form-input" min="0" max="10">
                            <span class="form-hint">对低置信度步骤进行 AI 看图增强（0-10 次）</span>
                        </div>

                        <div class="form-group" id="fps-group" :class="{ visible: useVideo }">
                            <label class="form-label">抽帧频率 (FPS)</label>
                            <input v-model.number="fps" type="number" class="form-input" min="0.1" max="10" step="0.1"
                                style="display:block;width:100%;">
                            <span class="form-hint">视频上传模式下的抽帧频率，默认 1 帧/秒</span>
                        </div>

                        <label class="checkbox-group">
                            <input v-model="useVideo" type="checkbox">
                            <div class="checkbox-label">
                                <strong>视频上传模式</strong>
                                <span>直接上传视频给 AI 识别（更准确，费用更高）</span>
                            </div>
                        </label>

                        <label class="checkbox-group">
                            <input v-model="webSearch" type="checkbox">
                            <div class="checkbox-label">
                                <strong>联网搜索增强</strong>
                                <span>自动搜索相关信息，丰富文档内容（需提前开通）</span>
                            </div>
                        </label>
                    </div>
                </div>

                <div class="card history-card">
                    <div class="card-header">
                        <i data-lucide="history">
                            <svg t="1773047101420" class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="5254" width="200" height="200"><path d="M762.805186 140.938939c-14.335497-9.66922-33.725102-5.887081-43.373857 8.398274-9.648754 14.295588-5.897314 33.714869 8.398274 43.373857 106.369609 71.852468 169.864736 191.267185 169.864736 319.445496 0 212.414831-172.802648 385.217479-385.217479 385.217479S127.259382 724.571397 127.259382 512.156566c0-128.178311 63.494103-247.593028 169.864736-319.445496 14.295588-9.658987 18.047028-29.078269 8.398274-43.373857-9.658987-14.285355-29.088502-18.067494-43.373857-8.398274C138.575102 224.432539 64.791655 363.206162 64.791655 512.156566c0 246.851131 200.834074 447.685205 447.685205 447.685205S960.162066 759.007697 960.162066 512.156566C960.162066 363.206162 886.377596 224.432539 762.805186 140.938939z" fill="#999999" p-id="5255"></path><path d="M401.003 64.47136c-17.253966 0-31.234375 13.980409-31.234375 31.233352l0 30.470989c0 17.253966 13.980409 31.234375 31.234375 31.234375s31.234375-13.980409 31.234375-31.234375L432.237375 95.704712C432.236352 78.450746 418.256966 64.47136 401.003 64.47136z" fill="#999999" p-id="5256"></path><path d="M623.950721 64.47136c-17.253966 0-31.233352 13.980409-31.233352 31.233352l0 30.470989c0 17.253966 13.980409 31.234375 31.233352 31.234375s31.234375-13.980409 31.234375-31.234375L655.185097 95.704712C655.184073 78.450746 641.204687 64.47136 623.950721 64.47136z" fill="#999999" p-id="5257"></path><path d="M426.012603 227.493248c11.214413 18.047028 41.970904 48.589648 86.157265 48.589648 43.963281 0 75.105558-30.318516 86.574774-48.223305 9.222035-14.396895 5.03262-33.358759-9.242502-42.763966-14.304797-9.405207-33.593096-5.398964-43.159986 8.764618-0.132006 0.193405-13.614066 19.754926-34.172287 19.754926-19.989263 0-32.423457-18.098193-33.267685-19.36914-9.160637-14.427594-28.264741-18.799158-42.834574-9.770528C421.416935 193.584973 416.912341 212.841549 426.012603 227.493248z" fill="#999999" p-id="5258"></path><path d="M510.781242 335.164502c-17.253966 0-31.233352 13.980409-31.233352 31.233352l0 208.225415c0 0.63445 0.149403 1.227967 0.187265 1.853208 0.067538 1.115404 0.148379 2.217505 0.333598 3.314489 0.168846 1.00898 0.416486 1.978051 0.679475 2.951215 0.258896 0.954745 0.529049 1.895163 0.87595 2.821255 0.36839 0.981351 0.801249 1.916653 1.26276 2.847861 0.431835 0.876973 0.880043 1.734504 1.393743 2.569522 0.532119 0.860601 1.115404 1.670036 1.727341 2.472308 0.610914 0.805342 1.235131 1.588171 1.926886 2.336208 0.688685 0.74292 1.424442 1.420349 2.181689 2.093684 0.741897 0.659009 1.484817 1.303692 2.298346 1.89721 0.899486 0.657986 1.850138 1.222851 2.819209 1.783623 0.544399 0.314155 1.00898 0.714268 1.577938 0.998747l208.225415 104.113219c4.484128 2.236947 9.252735 3.304256 13.94971 3.304256 11.44875 0 22.479991-6.334265 27.959795-17.274432 7.706519-15.433504 1.454118-34.192753-13.970176-41.909505l-190.961216-95.480608L542.015617 366.397854C542.015617 349.143888 528.035208 335.164502 510.781242 335.164502z" fill="#999999" p-id="5259"></path></svg>
                        </i>
                        <h2>历史记录</h2>
                    </div>
                    <div class="card-body">
                        <div class="history-list">
                            <div v-if="history.length === 0" class="history-empty">暂无历史记录</div>

                            <div v-for="record in history" :key="record.id" class="history-item" @click="openHistoryRecord(record.id)">
                                <div class="history-header">
                                    <span class="history-title" :title="record.video_name" v-text="record.video_name"></span>
                                    <button class="history-delete" title="删除" @click.stop="removeHistoryRecord(record.id)">
                                        <i data-lucide="trash-2" style="width:14px;height:14px;"></i>
                                    </button>
                                </div>
                                <div class="history-meta">
                                    <span class="history-badge" :class="modeBadgeClass(record.mode)" v-text="modeLabel(record.mode)"></span>
                                    <span v-text="`${record.steps_count || 0} 步`"></span>
                                    <span v-text="record.timestamp"></span>
                                </div>
                            </div>
                        </div>

                        <button class="btn btn-secondary btn-sm history-refresh" :class="{ loading: loadingHistory }"
                            @click="loadHistory">
                            <i data-lucide="refresh-cw" class="refresh-icon">
                                <svg t="1773047236264" class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="7144" width="200" height="200"><path d="M698.569 531.322a39.825 39.825 0 0 0-23.898 7.949c-17.702 13.216-21.34 38.28-8.124 55.982l95.716 128.212c7.854 10.521 19.893 16.073 32.084 16.073a39.825 39.825 0 0 0 23.898-7.949c17.702-13.216 21.34-38.28 8.124-55.982l-95.716-128.212c-7.853-10.521-19.892-16.074-32.084-16.073z" fill="#333333" p-id="7145"></path><path d="M922.498 563.818a39.825 39.825 0 0 0-23.898 7.949l-128.212 95.716c-17.703 13.216-21.34 38.28-8.124 55.982 7.854 10.521 19.893 16.073 32.084 16.073a39.825 39.825 0 0 0 23.898-7.949l128.212-95.716c17.702-13.216 21.34-38.28 8.124-55.982-7.854-10.521-19.893-16.074-32.084-16.073zM229.652 282.148a39.825 39.825 0 0 0-23.898 7.949c-17.702 13.216-21.34 38.28-8.124 55.982l95.716 128.212c7.854 10.521 19.893 16.073 32.084 16.073a39.825 39.825 0 0 0 23.898-7.949c17.702-13.216 21.34-38.28 8.124-55.982l-95.716-128.212c-7.854-10.521-19.892-16.074-32.084-16.073z" fill="#333333" p-id="7146"></path><path d="M229.652 282.148a39.825 39.825 0 0 0-23.898 7.949L77.542 385.813c-17.702 13.216-21.34 38.28-8.124 55.982 7.854 10.521 19.893 16.073 32.084 16.073a39.825 39.825 0 0 0 23.898-7.949l128.213-95.716c17.702-13.216 21.34-38.28 8.124-55.982-7.855-10.521-19.893-16.073-32.085-16.073z" fill="#333333" p-id="7147"></path><path d="M614.968 763.65c-44.13 18.171-94.005 25.121-146.168 16.968C353.747 762.636 261.364 670.253 243.381 555.2c-9.681-61.936 1.932-120.646 28.337-170.344l-58.657-58.657c-40.139 64.442-60.11 142.746-50.806 226.152 17.993 161.306 148.088 291.401 309.394 309.394 62.041 6.92 121.259-2.357 174.048-24.083 26.535-10.921 33.625-45.203 13.335-65.493l-0.098-0.098c-11.555-11.555-28.854-14.643-43.966-8.421zM409.033 260.35c44.131-18.171 94.007-25.122 146.169-16.968 115.051 17.985 207.431 110.365 225.416 225.416 9.682 61.935-1.931 120.646-28.337 170.346l58.658 58.658c40.139-64.443 60.109-142.747 50.805-226.155-17.993-161.305-148.087-291.399-309.391-309.391-62.042-6.92-121.26 2.356-174.05 24.082-26.535 10.921-33.625 45.203-13.335 65.493l0.099 0.099c11.555 11.554 28.854 14.642 43.966 8.42z" fill="#333333" p-id="7148"></path></svg>
                            </i>
                            刷新
                        </button>
                    </div>
                </div>
            </div>

            <div class="content-area">
                <div class="card">
                    <div class="card-header">
                        <i data-lucide="upload">
                            <svg t="1773047520242" class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="12213" width="200" height="200"><path d="M565.333333 779.914667l51.445334-54.912a31.733333 31.733333 0 0 1 45.226666-1.226667 32.64 32.64 0 0 1 1.216 45.770667l-97.418666 104a37.034667 37.034667 0 0 1-52.821334 1.397333l-108.362666-104.202667a32.64 32.64 0 0 1-1.152-45.770666 31.733333 31.733333 0 0 1 45.248-1.173334L501.333333 774.421333V512.074667c0-17.877333 14.325333-32.373333 32-32.373334s32 14.506667 32 32.373334v267.84zM512 138.666667c123.018667 0 228.213333 86.709333 259.424 206.88C864.298667 347.146667 938.666667 426.090667 938.666667 522.688c0 97.6-75.914667 177.173333-170.133334 177.173333-17.674667 0-32-14.496-32-32.373333 0-17.877333 14.325333-32.373333 32-32.373333 58.357333 0 106.133333-50.08 106.133334-112.426667 0-62.336-47.776-112.416-106.133334-112.416-5.856 0-11.626667 0.501333-17.301333 1.482667-17.621333 3.050667-34.304-9.098667-37.024-26.986667C698.346667 280.693333 612.714667 203.424 512 203.424c-73.834667 0-140.928 41.536-177.376 107.861333a31.914667 31.914667 0 0 1-30.122667 16.576 140.373333 140.373333 0 0 0-9.568-0.32c-80.149333 0-145.6 68.586667-145.6 153.781334 0 85.184 65.450667 153.792 145.6 153.792 17.674667 0 32 14.496 32 32.373333 0 17.877333-14.325333 32.373333-32 32.373333C178.912 699.861333 85.333333 601.770667 85.333333 481.322667c0-118.314667 90.293333-215.061333 203.456-218.453334C338.090667 186.24 421.013333 138.666667 512 138.666667z" fill="#000000" p-id="12214"></path></svg>
                        </i>
                        <h2>上传视频</h2>
                    </div>
                    <div class="card-body">
                        <div class="batch-area">
                            <input ref="batchFileInput" type="file" accept="video/*" multiple style="display:none;"
                                @change="handleBatchSelect">
                            <div class="upload-area" :class="batchUploadClass" @click="triggerBatchSelect"
                                @dragover.prevent="batchDragOver = true" @dragleave="batchDragOver = false"
                                @drop.prevent="handleBatchDrop">
                                <div class="upload-icon" style="width:56px;height:56px;">
                                    <i data-lucide="folder-plus">
                                        <svg t="1773047334432" class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="9237" width="200" height="200"><path d="M693.748069 172.723618H146.000839C77.597461 172.723618 21.95045 228.370629 21.95045 296.774007v603.175604c0 68.403378 55.647011 124.050389 124.050389 124.050389h547.74723c68.403378 0 124.057928-55.647011 124.057929-124.050389V296.774007c0.007539-68.403378-55.647011-124.050389-124.057929-124.050389z m48.673229 727.225993a48.718464 48.718464 0 0 1-48.66569 48.658151H146.000839A48.718464 48.718464 0 0 1 97.342689 899.949611V296.774007a48.718464 48.718464 0 0 1 48.65815-48.65815h547.74723a48.718464 48.718464 0 0 1 48.66569 48.65815v603.175604z" p-id="9238"></path><path d="M877.991621 0H330.236852c-68.403378 0-124.057928 55.65455-124.057928 124.057928a37.696119 37.696119 0 1 0 75.392238 0A48.718464 48.718464 0 0 1 330.236852 75.392238h547.754769A48.718464 48.718464 0 0 1 926.657311 124.057928V727.233532a48.718464 48.718464 0 0 1-48.66569 48.658151 37.696119 37.696119 0 1 0 0 75.392238c68.403378 0 124.057928-55.647011 124.057929-124.050389V124.057928C1002.04955 55.65455 946.394999 0 877.991621 0zM599.696252 580.128196L316.997975 416.911539a37.696119 37.696119 0 0 0-56.544179 32.64484v326.433313a37.696119 37.696119 0 0 0 56.544179 32.64484l282.698277-163.209118a37.703658 37.703658 0 0 0 0-65.297218zM335.846035 710.700014V514.846057l169.609919 97.926978-169.609919 97.926979z" p-id="9239"></path></svg>
                                    </i>
                                </div>
                                <h3>点击选择多个视频文件</h3>
                                <p>支持 MP4, AVI, MOV, MKV, WMV, FLV, WebM, M4V 等格式</p>
                            </div>

                            <div v-if="batchFiles.length > 0" class="batch-file-list">
                                <div v-for="(item, index) in batchFiles" :key="`${item.filepath}-${index}`" class="batch-file-item"
                                    :class="item.status">
                                    <div class="batch-file-name">
                                        <i data-lucide="file-video"></i>
                                        <span :title="item.filename" v-text="item.filename"></span>
                                    </div>
                                    <span class="batch-file-status" :class="item.status" v-text="batchStatusText(item.status)"></span>
                                </div>
                            </div>

                            <button v-if="batchFiles.length > 0" class="btn btn-secondary" style="width:100%;margin-top:0.5rem;"
                                @click="clearBatchFiles">
                                <i data-lucide="x"></i> 清空列表
                            </button>
                        </div>

                        <button class="btn btn-primary btn-lg" style="width:100%;margin-top:1.5rem;" :disabled="!canAnalyze"
                            @click="startAnalyze">
                            <i data-lucide="play">
                                <svg t="1773047432191" class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="10327" width="200" height="200"><path d="M266.059294 139.565176l542.117647 331.294118a48.188235 48.188235 0 0 1 0 82.281412l-542.117647 331.294118A48.188235 48.188235 0 0 1 192.752941 843.294118V180.705882a48.188235 48.188235 0 0 1 73.306353-41.140706zM289.129412 266.480941v490.917647l197.812706-120.892235L690.657882 512 486.881882 387.493647 289.069176 266.480941z" fill="#000000" p-id="10328"></path></svg>
                            </i>
                            <span v-text="analyzeButtonText"></span>
                        </button>
                    </div>
                </div>

                <div v-if="hasAnyResult" class="results-grid">
                    <div v-if="hasBatchResult" class="card" style="grid-column: 1 / -1;">
                        <div class="card-header" style="justify-content: space-between;">
                            <div style="display:flex;align-items:center;gap:0.75rem;">
                                <i data-lucide="layers"></i>
                                <h2>批量处理结果</h2>
                            </div>
                            <button class="btn btn-primary btn-sm" @click="downloadBatchZip" :disabled="batchDownloadDisabled">
                                <i data-lucide="download">
                                    <svg t="1773048160888" class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="29603" width="200" height="200"><path d="M853.333333 1024c46.933333 0 85.333333-38.4 85.333334-85.333333v-85.333334h-85.333334v85.333334H170.666667v-85.333334H85.333333v85.333334c0 46.933333 38.4 85.333333 85.333334 85.333333h682.666666zM85.333333 341.333333h85.333334V85.333333h469.333333c4.266667 4.266667 17.066667 17.066667 29.866667 34.133334C729.6 174.933333 836.266667 281.6 853.333333 298.666667v42.666666h85.333334V290.133333c0-21.333333-8.533333-42.666667-25.6-59.733333L708.266667 25.6c-12.8-17.066667-34.133333-25.6-59.733334-25.6H170.666667C123.733333 0 85.333333 38.4 85.333333 85.333333v256z" fill="#303133" p-id="29604"></path><path d="M938.666667 341.333333H85.333333c-46.933333 0-85.333333 38.4-85.333333 85.333334v341.333333c0 46.933333 38.4 85.333333 85.333333 85.333333h853.333334c46.933333 0 85.333333-38.4 85.333333-85.333333v-341.333333c0-46.933333-38.4-85.333333-85.333333-85.333334z m0 426.666667H85.333333v-341.333333h853.333334v341.333333z" fill="#303133" p-id="29605"></path><path d="M273.066667 725.333333h187.733333v-51.2H349.866667l110.933333-166.4V469.333333H285.866667v51.2H384l-110.933333 166.4v38.4zM503.466667 725.333333h59.733333v-256h-59.733333v256zM622.933333 725.333333H682.666667v-85.333333h29.866666c55.466667 0 102.4-25.6 102.4-85.333333 0-64-46.933333-81.066667-102.4-81.066667h-89.6V725.333333z m59.733334-132.266666v-72.533334h25.6c29.866667 0 46.933333 8.533333 46.933333 34.133334 0 25.6-12.8 38.4-42.666667 38.4H682.666667z" fill="#303133" p-id="29606"></path></svg>
                                </i>
                                下载全部总结文档 (ZIP)
                            </button>
                        </div>
                        <div class="card-body results-panel">
                            <div class="batch-result-summary">
                                <div>总计: <span v-text="batchSummary.total"></span> 个视频</div>
                                <div>成功: <span style="color:oklch(0.4 0.15 145)" v-text="batchSummary.success"></span> 个</div>
                                <div>失败: <span style="color:oklch(0.5 0.15 25)" v-text="batchSummary.failed"></span> 个</div>
                            </div>

                            <div v-if="!batchResultData.results || batchResultData.results.length === 0" class="batch-empty">没有处理结果</div>

                            <div v-else class="batch-results">
                                <div v-for="result in batchResultData.results" :key="`${result.index}-${result.filename}`"
                                    class="batch-result-item" :class="result.success ? 'success' : 'failed'">
                                    <div class="batch-result-header">
                                        <span class="batch-result-title" v-text="result.filename"></span>
                                        <span class="batch-file-status" :class="result.success ? 'success' : 'failed'"
                                            v-text="result.success ? '成功' : '失败'"></span>
                                    </div>

                                    <template v-if="result.success">
                                        <p style="font-size:0.85rem;color:var(--muted-foreground);margin-bottom:0.5rem;">
                                            <span v-text="`识别到 ${result.steps_count || 0} 个步骤`"></span>
                                        </p>
                                        <button class="btn btn-secondary btn-sm"
                                            @click="downloadSingleFromBatch(result.output_dir, result.filename)">
                                            <i data-lucide="download"></i> 下载
                                        </button>
                                    </template>

                                    <p v-else style="font-size:0.85rem;color:#dc2626;" v-text="result.error || '处理失败'"></p>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div v-if="hasSingleResult" class="card">
                        <div class="card-header" style="justify-content: space-between;">
                            <div style="display:flex;align-items:center;gap:0.75rem;">
                                <i data-lucide="list-ordered">
                                    <svg t="1773048221630" class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="32357" width="200" height="200"><path d="M852.5824 219.9552H353.6896V280.576h498.8928c14.2336-0.2048 25.7024-15.9744 25.7024-30.3104 0-14.336-11.4688-30.0032-25.7024-30.3104z m-628.6336-48.5376c-43.4176 0-78.6432 35.2256-78.6432 78.6432s35.2256 78.6432 78.6432 78.6432 78.6432-35.2256 78.6432-78.6432-35.2256-78.6432-78.6432-78.6432z m0 104.8576c-14.5408 0-26.2144-11.6736-26.2144-26.2144 0-14.5408 11.6736-26.2144 26.2144-26.2144s26.2144 11.6736 26.2144 26.2144c0 14.5408-11.776 26.2144-26.2144 26.2144z m628.6336 205.824H353.6896V542.72h498.8928c14.2336-0.2048 25.7024-15.9744 25.7024-30.3104 0-14.336-11.4688-30.0032-25.7024-30.3104z m-628.6336-48.5376c-43.4176 0-78.6432 35.2256-78.6432 78.6432s35.2256 78.6432 78.6432 78.6432 78.6432-35.2256 78.6432-78.6432-35.2256-78.6432-78.6432-78.6432z m0 104.8576c-14.5408 0-26.2144-11.6736-26.2144-26.2144 0-14.5408 11.6736-26.2144 26.2144-26.2144s26.2144 11.6736 26.2144 26.2144c0 14.5408-11.776 26.2144-26.2144 26.2144z m0 0M852.5824 744.2432H353.6896V804.864h498.8928c14.2336-0.2048 25.7024-15.9744 25.7024-30.3104s-11.4688-30.0032-25.7024-30.3104z m-628.6336-48.5376c-43.4176 0-78.6432 35.2256-78.6432 78.6432s35.2256 78.6432 78.6432 78.6432 78.6432-35.2256 78.6432-78.6432-35.2256-78.6432-78.6432-78.6432z m0 104.8576c-14.5408 0-26.2144-11.6736-26.2144-26.2144s11.6736-26.2144 26.2144-26.2144 26.2144 11.6736 26.2144 26.2144-11.776 26.2144-26.2144 26.2144z m0 0" p-id="32358"></path></svg>
                                </i>
                                <h2>识别到的步骤</h2>
                            </div>
                            <button v-if="!isEditMode" class="btn btn-secondary btn-sm" @click="enterEditMode">
                                <i data-lucide="edit-2">
                                    <svg t="1773048259604" class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="33358" width="200" height="200"><path d="M882.553 207.403l-66.652-66.652L894.352 62.3s67.244-1.399 67.244 65.845l-79.043 79.258z m-727.882 34.214v627.609H782.28V443.348l89.658-89.658v515.536c0 49.518-40.14 89.658-89.658 89.658H154.671c-49.518 0-89.658-40.14-89.658-89.658V241.617c0-49.518 40.14-89.658 89.658-89.658h515.536l-89.658 89.658H154.671zM378.817 645.08v-67.244l33.622-33.622 67.199 67.199-33.578 33.667h-67.243z m458.965-392.789L502.021 588.967 434.853 521.8l336.219-336.219 66.71 66.71z" fill="#0F0F0F" p-id="33359"></path></svg>
                                </i> 编辑
                            </button>
                        </div>

                        <div v-if="!isEditMode" class="card-body results-panel">
                            <div v-if="!resultData.steps || resultData.steps.length === 0" class="empty-state">
                                <p>未识别到操作步骤</p>
                            </div>

                            <div v-for="(step, index) in resultData.steps" :key="`step-${index}`" class="step-item">
                                <div class="step-header">
                                    <span class="step-number" v-text="step.step || index + 1"></span>
                                    <span class="step-title" v-text="step.title || '未命名步骤'"></span>
                                    <span class="step-time" v-text="step.time || '00:00'"></span>
                                    <span v-if="step.confidence !== undefined && step.confidence !== null" class="confidence-badge"
                                        :class="confidenceClass(step.confidence)"
                                        v-text="`${confidenceLabel(step.confidence)} ${Number(step.confidence).toFixed(1)}`">
                                    </span>
                                </div>
                                <p class="step-description" v-text="step.description || ''"></p>
                            </div>
                        </div>

                        <div v-else class="card-body" style="max-height:500px;overflow-y:auto;">
                            <div class="edit-actions-bar">
                                <button class="btn btn-primary btn-sm" :disabled="savingSteps" @click="saveEditedSteps">
                                    <i data-lucide="check"></i>
                                    保存并重新生成
                                </button>
                                <button class="btn btn-secondary btn-sm" :disabled="savingSteps" @click="cancelEditMode">
                                    <i data-lucide="x"></i>
                                    取消
                                </button>
                            </div>

                            <div>
                                <div v-for="(step, index) in editedSteps" :key="`editing-${index}`" class="step-edit-item"
                                    :class="{ dragging: dragIndex === index, 'drag-over': dragOverIndex === index }" draggable="true"
                                    @dragstart="onStepDragStart(index)" @dragover.prevent="onStepDragOver(index)"
                                    @drop.prevent="onStepDrop(index)" @dragend="onStepDragEnd">
                                    <div class="step-edit-header">
                                        <span class="step-drag-handle" title="拖拽调整顺序">
                                            <i data-lucide="grip-vertical" style="width:16px;height:16px;"></i>
                                        </span>
                                        <span class="step-edit-number" v-text="index + 1"></span>
                                        <input v-model="step.title" type="text" class="step-edit-input" placeholder="步骤标题">
                                        <input v-model="step.time" type="text" class="step-edit-time" placeholder="时间">
                                    </div>
                                    <textarea v-model="step.description" class="step-edit-textarea" placeholder="步骤描述"></textarea>
                                    <div class="step-edit-actions">
                                        <button class="btn btn-secondary btn-sm step-edit-delete" @click="removeEditedStep(index)">
                                            <i data-lucide="trash-2"></i>
                                            删除
                                        </button>
                                    </div>
                                </div>
                            </div>

                            <button class="step-add-btn" @click="addStep">
                                <i data-lucide="plus"></i>
                                添加新步骤
                            </button>
                        </div>
                    </div>

                    <div v-if="hasSingleResult" class="card" id="document-panel">
                        <div class="card-header" style="justify-content: space-between;">
                            <div style="display:flex;align-items:center;gap:0.75rem;">
                                <i data-lucide="file-text">
                                   <svg t="1773047879981" class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="18808" width="200" height="200"><path d="M814.9 264.6L687 142c-11.3-10.8-26.3-16.3-41.5-15.8-0.5 0-1-0.1-1.5-0.1H332.6c-77.4 0-140.4 60.7-140.4 135.2v501.3c0 74.6 63 135.2 140.4 135.2h358.7c77.4 0 140.4-60.7 140.4-135.2V305.3c0.7-15-5.2-29.6-16.8-40.7zM623.1 181c0-13.4 10.8-19.1 14.1-20.5 3-1.3 6.6-2.1 10.5-2.1 5.7 0 11.8 1.9 17.1 6.9l127.9 122.6c6.7 6.4 8.7 15.2 5.3 23.6-2.9 7.1-10.3 14.7-22.7 14.7h-128c-13.4 0-24.2-10.1-24.2-22.6V181z m176.4 581.7c0 56.8-48.5 103-108.2 103H332.6c-59.7 0-108.2-46.2-108.2-103V261.3c0-56.8 48.5-103 108.2-103h263.1c-3.2 6.9-4.9 14.6-4.9 22.6v122.6c0 30.2 25.3 54.8 56.5 54.8h127.9c8.6 0 16.9-1.9 24.3-5.3v409.7z" fill="#333333" p-id="18809"></path><path d="M498.4 424.9H325.1c-8.9 0-16.1-7.2-16.1-16.1s7.2-16.1 16.1-16.1h173.4c8.9 0 16.1 7.2 16.1 16.1s-7.3 16.1-16.2 16.1zM696.8 559.5H325.1c-8.9 0-16.1-7.2-16.1-16.1s7.2-16.1 16.1-16.1h371.7c8.9 0 16.1 7.2 16.1 16.1s-7.2 16.1-16.1 16.1zM696.8 694.2H325.1c-8.9 0-16.1-7.2-16.1-16.1s7.2-16.1 16.1-16.1h371.7c8.9 0 16.1 7.2 16.1 16.1s-7.2 16.1-16.1 16.1z" fill="#EF7F1A" p-id="18810"></path></svg>
                                </i>
                                <h2>生成的总结文档</h2>
                            </div>
                            <button class="btn btn-primary btn-sm" @click="downloadSingleZip">
                                <i data-lucide="download"></i>
                                下载完整总结文档 (ZIP)
                            </button>
                        </div>
                        <div class="card-body results-panel">
                            <div class="markdown-content" v-html="renderedMarkdown"></div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div class="progress-overlay" :class="{ active: progressVisible }">
            <div class="progress-card">
                <div class="progress-spinner"></div>
                <h3 v-text="progressTitle"></h3>
                <p v-text="progressText"></p>
            </div>
        </div>

        <div class="error-toast" :class="{ show: showErrorToast }">
            <i data-lucide="alert-circle"></i>
            <span v-text="errorMessage"></span>
        </div>
    </div>
</template>

<script>
import DOMPurify from "dompurify";
import { createIcons } from "lucide";
import { marked } from "marked";

const VALID_VIDEO_EXTENSIONS = new Set([
    "mp4", "avi", "mov", "mkv", "wmv", "flv", "webm", "m4v", "mpg", "mpeg", "3gp", "ts", "m2ts"
]);

const WEB_SEARCH_ERROR_HINTS = ["toolnotopen", "web search", "\u8054\u7f51\u641c\u7d22"];

const basename = (pathValue) => {
    if (!pathValue) {
        return "";
    }
    const parts = String(pathValue).split(/[\\/]/).filter(Boolean);
    return parts.length > 0 ? parts[parts.length - 1] : "";
};

const isValidVideo = (filename) => {
    const ext = String(filename || "").split(".").pop().toLowerCase();
    return VALID_VIDEO_EXTENSIONS.has(ext);
};

const clone = (value) => JSON.parse(JSON.stringify(value));

export default {
    data() {
        return {
            apiKey: "",
            whisperModel: "base",
            maxVision: 10,
            useVideo: false,
            webSearch: false,
            fps: 1,

            isAnalyzing: false,
            loadingHistory: false,
            savingSteps: false,

            batchFiles: [],

            resultData: null,
            batchResultData: null,
            history: [],

            isEditMode: false,
            editedSteps: [],
            dragIndex: null,
            dragOverIndex: null,

            batchDragOver: false,

            progressVisible: false,
            progressTitle: "处理中...",
            progressText: "请稍候",

            errorMessage: "",
            showErrorToast: false,
            errorTimer: null,

            iconFrame: null,
            batchProgressTimer: null
        };
    },

    computed: {
        canAnalyze() {
            if (this.isAnalyzing) {
                return false;
            }
            return this.batchFiles.length > 0;
        },

        analyzeButtonText() {
            if (this.isAnalyzing) {
                return "批量处理中...";
            }
            return "开始批量分析";
        },

        hasSingleResult() {
            return Boolean(this.resultData);
        },

        hasBatchResult() {
            return Boolean(this.batchResultData);
        },

        hasAnyResult() {
            return this.hasSingleResult || this.hasBatchResult;
        },

        batchUploadClass() {
            return {
                dragover: this.batchDragOver
            };
        },

        batchSummary() {
            return this.batchResultData?.summary || { total: 0, success: 0, failed: 0 };
        },

        batchDownloadDisabled() {
            return (this.batchResultData?.results || []).every((item) => !item.success);
        },

        renderedMarkdown() {
            if (!this.resultData?.markdown) {
                return "";
            }

            const outputDirName = basename(this.resultData.output_dir);
            const baseUrl = outputDirName ? `/output/${encodeURIComponent(outputDirName)}/` : "";

            const markdownText = String(this.resultData.markdown).replace(
                /!\[(.*?)\]\((images\/.*?)\)/g,
                (_match, alt, imgPath) => `![${alt}](${baseUrl}${imgPath})`
            );

            const rawHtml = marked.parse(markdownText, {
                gfm: true,
                breaks: true
            });

            return DOMPurify.sanitize(rawHtml);
        }
    },

    mounted() {
        this.renderIcons();
        this.loadHistory();
    },

    updated() {
        this.renderIcons();
    },

    beforeUnmount() {
        this.stopBatchProgressPolling();

        if (this.errorTimer) {
            clearTimeout(this.errorTimer);
        }
        if (this.iconFrame) {
            cancelAnimationFrame(this.iconFrame);
        }
    },

    methods: {
        renderIcons() {
            if (this.iconFrame) {
                cancelAnimationFrame(this.iconFrame);
            }
            this.iconFrame = requestAnimationFrame(() => createIcons());
        },

        showProgress(title, text) {
            this.progressTitle = title || "处理中...";
            this.progressText = text || "请稍候";
            this.progressVisible = true;
        },

        hideProgress() {
            this.progressVisible = false;
        },

        showError(message) {
            this.errorMessage = message || "操作失败";
            this.showErrorToast = true;

            if (this.errorTimer) {
                clearTimeout(this.errorTimer);
            }
            this.errorTimer = setTimeout(() => {
                this.showErrorToast = false;
            }, 5000);
        },

        async fetchJson(url, options = {}) {
            const response = await fetch(url, options);
            const data = await response.json().catch(() => ({}));

            if (!response.ok || data.error) {
                throw new Error(data.error || `请求失败 (${response.status})`);
            }

            return data;
        },

        async fetchBlob(url, options = {}) {
            const response = await fetch(url, options);
            if (!response.ok) {
                let message = `下载失败 (${response.status})`;
                try {
                    const data = await response.json();
                    if (data?.error) {
                        message = data.error;
                    }
                } catch (_error) {
                    // ignore json parse failure
                }
                throw new Error(message);
            }
            return response.blob();
        },

        triggerBatchSelect() {
            this.$refs.batchFileInput?.click();
        },

        async handleBatchSelect(event) {
            const files = event?.target?.files;
            if (!files || files.length === 0) {
                return;
            }
            await this.uploadBatchFiles(files);
            event.target.value = "";
        },

        async handleBatchDrop(event) {
            this.batchDragOver = false;
            const files = event?.dataTransfer?.files;
            if (!files || files.length === 0) {
                return;
            }
            await this.uploadBatchFiles(files);
        },

        async uploadBatchFiles(fileList) {
            const files = Array.from(fileList || []).filter((file) => isValidVideo(file.name));
            if (files.length === 0) {
                this.showError("没有可用的视频文件，请检查格式");
                return;
            }

            const formData = new FormData();
            files.forEach((file) => formData.append("files", file));

            this.showProgress("上传中", "正在上传批量视频文件...");
            try {
                const data = await this.fetchJson("/upload_batch", {
                    method: "POST",
                    body: formData
                });

                if (Array.isArray(data.errors) && data.errors.length > 0) {
                    this.showError(data.errors.join("；"));
                }

                const uploadedItems = (data.uploaded || []).map((item) => ({
                    filename: item.filename,
                    filepath: item.filepath,
                    status: "pending",
                    error: ""
                }));

                this.batchFiles = [...this.batchFiles, ...uploadedItems];
            } catch (error) {
                this.showError(`批量上传失败: ${error.message}`);
            } finally {
                this.hideProgress();
            }
        },

        clearBatchFiles() {
            this.batchFiles = [];
        },

        async startAnalyze() {
            if (!this.apiKey) {
                this.showError("请输入 ARK API Key");
                return;
            }
            await this.analyzeBatch();
        },

        startBatchProgressPolling() {
            this.stopBatchProgressPolling();
            this.pullBatchProgress();
            this.batchProgressTimer = setInterval(() => {
                this.pullBatchProgress();
            }, 1200);
        },

        stopBatchProgressPolling() {
            if (!this.batchProgressTimer) {
                return;
            }
            clearInterval(this.batchProgressTimer);
            this.batchProgressTimer = null;
        },

        buildProgressMessage(progress) {
            const total = Number(progress?.total) || this.batchFiles.length;
            const current = Number(progress?.current) || 0;
            const currentFile = String(progress?.current_file || "").trim();
            const stageMessage = String(progress?.message || "").trim()
                || "\u6b63\u5728\u9010\u4e2a\u5206\u6790\u89c6\u9891\uff0c\u8bf7\u7a0d\u5019...";

            const progressPart = total > 0
                ? `\u8fdb\u5ea6 ${Math.min(Math.max(current, 0), total)}/${total}`
                : "";
            const filePart = currentFile ? `\u5f53\u524d: ${currentFile}` : "";
            return [stageMessage, progressPart, filePart].filter(Boolean).join(" | ");
        },

        async pullBatchProgress() {
            try {
                const progress = await this.fetchJson("/batch_progress");
                const currentFile = String(progress.current_file || "");

                if (this.progressVisible) {
                    this.progressText = this.buildProgressMessage(progress);
                }

                if (!currentFile) {
                    return;
                }

                this.batchFiles = this.batchFiles.map((item) => {
                    if (item.status === "success" || item.status === "failed") {
                        return item;
                    }
                    if (item.filename === currentFile) {
                        return { ...item, status: "processing" };
                    }
                    return item;
                });
            } catch (_error) {
                // ignore polling failures
            }
        },

        async analyzeBatch() {
            if (this.batchFiles.length === 0) {
                this.showError("请先上传批量视频文件");
                return;
            }

            this.batchFiles = this.batchFiles.map((item) => ({
                ...item,
                status: "pending",
                error: ""
            }));

            this.isAnalyzing = true;
            this.showProgress("批量处理中", "正在逐个分析视频，请稍候...");
            this.startBatchProgressPolling();

            try {
                const data = await this.fetchJson("/analyze_batch", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        api_key: this.apiKey,
                        filepaths: this.batchFiles.map((item) => item.filepath),
                        whisper_model: this.whisperModel,
                        use_video: this.useVideo,
                        web_search: this.webSearch,
                        max_vision: this.maxVision,
                        fps: this.fps
                    })
                });

                const results = data.results || [];
                this.batchFiles = this.batchFiles.map((item, index) => {
                    const result = results[index];
                    if (!result) {
                        return item;
                    }
                    return {
                        ...item,
                        status: result.success ? "success" : "failed",
                        error: result.error || ""
                    };
                });

                if (results.some((item) => !item.success && this.isWebSearchError(item.error))) {
                    this.webSearch = false;
                }

                this.batchResultData = data;
                this.resultData = null;
                this.isEditMode = false;
                this.editedSteps = [];
                await this.loadHistory();
            } catch (error) {
                this.showError(`批量分析失败: ${error.message}`);
            } finally {
                this.stopBatchProgressPolling();
                this.isAnalyzing = false;
                this.hideProgress();
            }
        },

        isWebSearchError(errorMessage) {
            const normalized = String(errorMessage || "").toLowerCase();
            return WEB_SEARCH_ERROR_HINTS.some((hint) => normalized.includes(hint));
        },

        batchStatusText(status) {
            if (status === "success") {
                return "已完成";
            }
            if (status === "failed") {
                return "失败";
            }
            if (status === "processing") {
                return "处理中";
            }
            return "待处理";
        },

        modeBadgeClass(mode) {
            return mode === "video" ? "history-badge-video" : "history-badge-subtitle";
        },

        modeLabel(mode) {
            return mode === "video" ? "视频模式" : "字幕模式";
        },

        async loadHistory() {
            this.loadingHistory = true;
            try {
                const data = await this.fetchJson("/history");
                this.history = Array.isArray(data.history) ? data.history : [];
            } catch (error) {
                this.showError(`加载历史失败: ${error.message}`);
            } finally {
                this.loadingHistory = false;
            }
        },

        async openHistoryRecord(recordId) {
            this.showProgress("加载中", "正在读取历史记录...");
            try {
                const data = await this.fetchJson(`/history/${recordId}`);
                const record = data.record || {};
                this.resultData = {
                    steps: Array.isArray(record.steps) ? record.steps : [],
                    markdown: record.markdown || "",
                    output_dir: record.output_dir || "",
                    pdf_path: record.pdf_path || ""
                };
                this.batchResultData = null;
                this.isEditMode = false;
                this.editedSteps = [];
            } catch (error) {
                this.showError(`加载历史失败: ${error.message}`);
            } finally {
                this.hideProgress();
            }
        },

        async removeHistoryRecord(recordId) {
            if (!window.confirm("确定要删除这条历史记录吗？")) {
                return;
            }

            try {
                await this.fetchJson(`/history/${recordId}`, { method: "DELETE" });
                await this.loadHistory();
            } catch (error) {
                this.showError(`删除失败: ${error.message}`);
            }
        },

        confidenceClass(value) {
            const confidence = Number(value);
            if (confidence >= 0.7) {
                return "confidence-high";
            }
            if (confidence >= 0.4) {
                return "confidence-medium";
            }
            return "confidence-low";
        },

        confidenceLabel(value) {
            const confidence = Number(value);
            if (confidence >= 0.7) {
                return "高";
            }
            if (confidence >= 0.4) {
                return "中";
            }
            return "低";
        },

        enterEditMode() {
            if (!Array.isArray(this.resultData?.steps) || this.resultData.steps.length === 0) {
                this.showError("当前没有可编辑的步骤");
                return;
            }

            this.editedSteps = clone(this.resultData.steps).map((step, index) => ({
                ...step,
                step: index + 1,
                time: step.time || "00:00",
                title: step.title || "",
                description: step.description || ""
            }));
            this.isEditMode = true;
        },

        cancelEditMode() {
            this.isEditMode = false;
            this.editedSteps = [];
            this.dragIndex = null;
            this.dragOverIndex = null;
        },

        addStep() {
            this.editedSteps.push({
                step: this.editedSteps.length + 1,
                time: "00:00",
                title: "新步骤",
                description: "请输入步骤描述"
            });
        },

        removeEditedStep(index) {
            this.editedSteps.splice(index, 1);
            this.reindexEditedSteps();
        },

        reindexEditedSteps() {
            this.editedSteps = this.editedSteps.map((step, index) => ({
                ...step,
                step: index + 1
            }));
        },

        onStepDragStart(index) {
            this.dragIndex = index;
        },

        onStepDragOver(index) {
            this.dragOverIndex = index;
        },

        onStepDrop(index) {
            if (this.dragIndex === null || this.dragIndex === index) {
                this.dragOverIndex = null;
                return;
            }

            const [moved] = this.editedSteps.splice(this.dragIndex, 1);
            if (!moved) {
                this.dragOverIndex = null;
                return;
            }

            this.editedSteps.splice(index, 0, moved);
            this.reindexEditedSteps();
            this.dragIndex = null;
            this.dragOverIndex = null;
        },

        onStepDragEnd() {
            this.dragIndex = null;
            this.dragOverIndex = null;
        },

        async saveEditedSteps() {
            if (!this.apiKey) {
                this.showError("请输入 ARK API Key");
                return;
            }
            if (!this.resultData?.output_dir) {
                this.showError("缺少输出目录信息");
                return;
            }

            this.savingSteps = true;
            this.showProgress("重新生成中", "根据编辑后的步骤生成新文档...");
            try {
                const data = await this.fetchJson("/regenerate", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        api_key: this.apiKey,
                        steps: this.editedSteps,
                        output_dir: this.resultData.output_dir,
                        web_search: this.webSearch
                    })
                });

                this.resultData = data;
                this.isEditMode = false;
                this.editedSteps = [];
            } catch (error) {
                this.showError(`重新生成失败: ${error.message}`);
            } finally {
                this.savingSteps = false;
                this.hideProgress();
            }
        },

        triggerDownload(blob, filename) {
            const url = URL.createObjectURL(blob);
            const anchor = document.createElement("a");
            anchor.href = url;
            anchor.download = filename;
            anchor.click();
            URL.revokeObjectURL(url);
        },

        async downloadSingleZip() {
            const outputDirName = basename(this.resultData?.output_dir);
            if (!outputDirName) {
                this.showError("没有可下载的结果");
                return;
            }

            try {
                const blob = await this.fetchBlob(`/download_zip/${encodeURIComponent(outputDirName)}`);
                this.triggerDownload(blob, `${outputDirName}.zip`);
            } catch (error) {
                this.showError(`下载失败: ${error.message}`);
            }
        },

        async downloadSingleFromBatch(outputDir, filename) {
            const outputDirName = basename(outputDir);
            if (!outputDirName) {
                this.showError("下载路径无效");
                return;
            }

            try {
                const blob = await this.fetchBlob(`/download_zip/${encodeURIComponent(outputDirName)}`);
                const baseName = basename(filename).replace(/\.[^/.]+$/, "") || outputDirName;
                this.triggerDownload(blob, `${baseName}.zip`);
            } catch (error) {
                this.showError(`下载失败: ${error.message}`);
            }
        },

        async downloadBatchZip() {
            const outputDirs = (this.batchResultData?.results || [])
                .filter((item) => item.success && item.output_dir)
                .map((item) => item.output_dir);

            if (outputDirs.length === 0) {
                this.showError("没有可下载的批量结果");
                return;
            }

            try {
                const blob = await this.fetchBlob("/download_batch_zip", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ output_dirs: outputDirs })
                });
                this.triggerDownload(blob, "batch_results.zip");
            } catch (error) {
                this.showError(`下载失败: ${error.message}`);
            }
        }
    }
};
</script>
