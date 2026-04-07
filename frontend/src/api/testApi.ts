import { getOpinions } from './databaseApi';

export async function testApi() {
  try {
    console.log('测试API调用...');
    const response = await getOpinions(0, 5);
    console.log('API响应:', response);
    console.log('总记录数:', response.total);
    console.log('记录数:', response.items?.length);
    console.log('第一条记录:', response.items?.[0]);
    return response;
  } catch (error) {
    console.error('API调用失败:', error);
    throw error;
  }
}
