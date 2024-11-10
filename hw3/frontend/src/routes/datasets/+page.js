import { PUBLIC_API_URL } from '$env/static/public';

export async function load({ fetch, url }) {
	const page = url.searchParams.get('page') || 1;

	const res = await fetch(
		`${PUBLIC_API_URL}/api/document_set/?page=${page}&pageSize=12`
	);
	console.log(res.status)
	const data = await res.json();

	return {
		data
	}
}